---
name: yt-dlp-video-download
description: 用 yt-dlp 通过链接下载 YouTube 等站点的视频/音频。默认下载最佳画质 mp4 视频，支持播放列表批量、字幕下载、封面与元数据嵌入。适用于用户给出视频/播放列表链接要求下载的场景。
alwaysApply: false
---

# 视频链接下载（yt-dlp）

通过链接下载 YouTube 等站点的视频或音频。默认产出**最佳画质 mp4 视频**，支持播放列表批量、字幕下载、封面与元数据嵌入。

## 何时使用

- 用户给出视频链接 / 播放列表链接，要求下载
- 需要批量下载整个播放列表或频道
- 需要字幕、封面、元数据
- 需要仅提取音频

## 一、环境准备

```bash
# yt-dlp 未预装，需安装；二进制落在 ~/.local/bin（不在 PATH）
pip install -q --break-system-packages yt-dlp
YTDLP=~/.local/bin/yt-dlp
$YTDLP --version

# ffmpeg 已预装，用于合并流、嵌入封面
which ffmpeg
```

安装后统一用绝对路径 `$HOME/.local/bin/yt-dlp` 调用，避免 PATH 问题。

## 二、沙箱硬限制（务必先理解，否则任务必失败）

这些是本机 Linux 沙箱的真实限制，已验证：

1. **每次 bash 调用最多 45 秒**（timeout_ms 上限 45000）。超时会被强杀。
2. **后台进程不能保活**。`nohup ... &`、`setsid`、`disown` 全都没用——调用返回时沙箱会杀掉所有子进程（bwrap `--die-with-parent`）。所有工作必须在**单次调用的 45 秒内**完成，或拆成多次调用分段完成。
3. **用户的输出目录禁止删除文件**。`rm` 返回 `Operation not permitted`；但 `: > file`（截断为 0 字节）可以，能回收空间。
4. **`/tmp` 在一次会话内持久且快**（本地磁盘，多 GB/s），跨 bash 调用保留；会话结束后清空。**但 `/tmp` 只有约 9.6G，其中系统占 4.9G，实际可用约 4.7G**。
5. **输出目录（挂载点）读写都约 6.6 MB/s**，很慢。大文件写入需要分块。

**核心策略：下载和后处理都在 `/tmp` 做（快），完事再用分块 `dd` 拷到输出目录（慢但可控）。**

## 三、标准流程

### 步骤 0：探查链接

先列出播放列表内容，判断规模（时长、集数），据此决定是否需要向用户确认。

```bash
$YTDLP --flat-playlist \
  --print "%(playlist_index)s | %(id)s | %(duration)s | %(title)s" \
  "<链接>" 2>&1 | head -60
```

单个视频时 `--flat-playlist` 也可用，或直接 `--print "%(title)s | %(duration)s"`。

如果目标内容很大（如累计 >1 小时或多个 GB），**先用 AskUserQuestion 向用户确认格式与附加内容**，再开始下载。

### 步骤 1：确认输出目录与格式

- 输出目录 = 用户选择的文件夹（挂载点）。
- 默认格式：`bv*+ba/b`（最佳视频+最佳音频，合并为 mp4）。若用户要音频，用 `bestaudio[ext=m4a]`。

**格式选择要点（重要）**：
- 优先 DASH 自适应流（`--format "bv*+ba/b"` 会自动选）。分开下载视频流和音频流后由 ffmpeg 合并，最可靠。
- **避开 HLS/m3u8 流**（`-F` 列表里 protocol 列为 `m3u8` 的，如某些 `234/233` 格式）。这类流会报告**错误的完整大小**，且容易在下到一半时截断。
- 纯音频推荐 `--format "140/bestaudio[ext=m4a]/bestaudio"`（140 = m4a 129k/44kHz，稳定）。
- 若确实需要指定分辨率，用 `-F` 查出视频流 ID（如 137=1080p、136=720p）再 `--format "137+140"`。

### 步骤 2：分块下载（≤40s/次，靠 --continue 续传）

因为 45s 限制，用一个带 `timeout` 的脚本反复调用来完成下载。**关键：用 `--continue` 断点续传，且不要加 `--no-part`**（`--no-part` 会让截断的文件被误判为"已下载完成"）。

```bash
mkdir -p /tmp/dl
cat > /tmp/dl.sh << 'SH'
#!/bin/bash
YTDLP=$HOME/.local/bin/yt-dlp
cd /tmp/dl
timeout 40 $YTDLP --no-cache-dir \
  --format "bv*+ba/b" \
  --output "%(playlist_index)02d.%(ext)s" \
  --merge-output-format mp4 \
  --continue --no-overwrites --no-mtime --newline \
  --retries 10 --fragment-retries 10 --retry-sleep 5 \
  --download-archive /tmp/dl/archive.txt \
  "$@" "<链接>"
SH
chmod +x /tmp/dl.sh
```

反复调用直到完成：

```bash
bash /tmp/dl.sh --playlist-items 1        # 单集
bash /tmp/dl.sh --playlist-items 2,3,4    # 多集
```

每次调用结束看 `.part` 文件是否增长来判断进度。`--download-archive` 记录已完成的，重复调用会跳过。

**磁盘管理**：`/tmp` 只有 ~4.7G 可用。大批量时**逐集处理**——下完一集、后处理、拷走、删源，再下一集。监视 `df -h /tmp`。已处理完的源文件可 `rm`（/tmp 里能删）。

### 步骤 3：后处理（本地 /tmp 做，同样分块）

抽封面、嵌元数据等都在本地做，再拷到输出目录（挂载点做这些很慢）。

**封面坑**：YouTube 缩略图是 webp，**无法嵌入 mp4/m4a 容器**，必须先转 png/jpg：

```bash
ffmpeg -y -loglevel error -i cover.webp cover.png
```

合并视频时顺带嵌入封面与元数据（`ffmpeg` 合并）：

```bash
# 视频：合并 video+audio，嵌入封面，写元数据
ffmpeg -y -i video.mp4 -i audio.m4a -i cover.png \
  -map 0:v -map 1:a -map 2 -c copy -disposition:v:1 attached_pic \
  -metadata title="标题" -metadata artist="作者" \
  out.mp4
```

仅音频（m4a / mp3）嵌入封面与标签：

```bash
# m4a
ffmpeg -y -i a.m4a -i cover.png -map 0:a -map 1 -c copy \
  -disposition:v attached_pic -metadata title="标题" out.m4a
# mp3（封面需 -id3v2_version 3）
ffmpeg -y -i a.mp3 -i cover.png -map 0:a -map 1 -c:a copy -c:v png \
  -id3v2_version 3 -disposition:v attached_pic -metadata title="标题" out.mp3
```

### 步骤 4：分块拷到输出目录（关键）

挂载点写入慢（~6.6MB/s），单个大文件会超过 45s。用**可续传的分块 `dd`**，每轮约 160MB，反复调用直到 `目标大小 >= 源大小`：

```bash
cat > /tmp/copy.sh << 'SH'
#!/bin/bash
MNT="<输出目录的沙箱路径>"     # 见下方路径映射
START=$(date +%s)
for i in "$@"; do
  src="/tmp/full/$i.mp4"; dst="$MNT/$i.mp4"
  ss=$(stat -c%s "$src"); ds=$(stat -c%s "$dst" 2>/dev/null || echo 0)
  [ "$ds" -ge "$ss" ] && { echo "✓ $i 已完成"; continue; }
  sk=$((ds/1048576))
  dd if="$src" of="$dst" bs=1M skip=$sk seek=$sk conv=notrunc count=160 2>&1 | tail -1
  [ $(( $(date +%s) - START )) -gt 33 ] && { echo "(本轮时间到)"; exit 0; }
done
echo "=== 复制完成 ==="
SH
chmod +x /tmp/copy.sh
bash /tmp/copy.sh 01 02   # 反复调用直到全部 ✓
```

`skip`/`seek` + `conv=notrunc` 实现断点续传；即使被 45s 强杀，下一轮也能接着写。

### 步骤 5：校验

```bash
# 时长、编码、流、标签
ffprobe -v error -show_entries format=duration -of csv=p=0 "文件"
ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "文件"
ffprobe -v error -show_entries format_tags=title -of csv=p=0 "文件"

# 字节级一致（源 vs 落盘）
md5sum /tmp/full/01.mp4 "<输出目录>/01.mp4"
```

## 四、路径映射

文件工具（Read/Write）看到的是宿主机路径，bash 看到的是挂载路径，需换算：

- 用户输出目录：`/Users/<user>/<目录>` ↔ `/sessions/<session>/mnt/<目录>/`
- 临时输出目录：`.../local_xxxx/outputs` ↔ `/sessions/<session>/mnt/outputs/`
- 上传的文件：`.../uploads` ↔ `/sessions/<session>/mnt/uploads/`（只读）
- skills：`/var/folders/.../skills` ↔ `/sessions/<session>/mnt/.claude/skills/`（只读）

具体路径以 system prompt 里的「Shell access」段落为准。

## 五、附加能力

**字幕**：

```bash
--write-subs --sub-langs "zh-Hans,zh,en" --convert-subs srt   # 手动字幕
--write-auto-subs --sub-langs "zh-Hans,en"                     # 自动字幕
```

**播放列表批量**：`--playlist-items 1,3,5-8` 选段；`--playlist-start/--playlist-end` 范围。批量前务必先用 `--flat-playlist` 探查，并向用户确认规模。

**只要音频**：`--format "140/bestaudio[ext=m4a]/bestaudio"`。

## 六、常见坑（血泪清单）

- ❌ **不要加 `--no-part`**：截断的文件会被误判为已完成。
- ❌ **不要用后台进程**：`nohup &` / `setsid` / `disown` 都会被沙箱杀掉。
- ❌ **不要选 m3u8/HLS 格式**：报告大小错误、易截断。用 DASH 自适应流。
- ❌ **webp 封面不能直接嵌入**：先转 png。
- ❌ **不要在挂载点跑重的后处理**：先在 /tmp 做好再拷。
- ❌ **`rm` 输出目录会失败**：残留文件只能 `: > file` 清空，最后告知用户手动删除。
- ❌ **glob 误删**：`rm 02_*.mp3` 会连 `02_full.mp3` 一起删掉。删除前用精确文件名列清单。
- ⚠️ **写文件用原子方式**：先写 `.tmp`/`.part` 再 `mv`，被强杀时不会留下半截成品。
- ⚠️ **并发转码/下载数**：4 路并行时单项约 35-40s，容易贴上限；稳妥用 3 路，或给每个子任务套 `timeout 39` 让脚本干净退出。
- ⚠️ **/tmp 空间**：约 4.7G 可用，边做边清。

## 七、完成后的交代

- 用 `computer://` 链接把成品给用户（不要链接文件夹）。
- 若有无法删除的 0 字节残留，明确告知用户手动清理。
- 简要说明格式、大小、时长、附加内容，不要长篇解释过程。
