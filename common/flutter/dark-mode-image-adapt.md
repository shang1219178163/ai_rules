---
name: dark-mode-image-adapt
description: >-
  暗黑模式图片适配：从 Figma 导入深色切图，按浅色资源配对落盘，并用 Assets.xxx.orLight 切换。
  Use when the user pastes a Figma URL and asks to import dark images, 导入暗黑模式图片,
  暗黑模式图片适配, orLight, _light 后缀, 深色/浅色切图, or matching dark assets to existing light files.
alwaysApply: false
---

# 暗黑模式图片适配

从 Figma 导入暗黑切图，配对已有浅色资源。深色是默认文件名，浅色才带 `_light`。

## 铁律

1. **文件名**：暗黑 = 浅色去掉 `_light`。禁止 `*_dark`、禁止另起目录。
2. **目录**：与对应浅色图同一目录。
3. **格式**：与浅色一致（浅色 `.png` → 深色 `.png`；浅色 `.webp` → 深色 `.webp`）。
4. **调用**：`Assets.xxx.orLight`，不要写 `Assets.xxxLight`。

| 浅色 | 暗黑 | 调用 |
|------|------|------|
| `assets/images/mine/v2/ic_personal_light.png` | `.../ic_personal.png` | `Assets.v2IcPersonal.orLight` |
| `assets/images/mine/v2/bg_wave_light.webp` | `.../bg_wave.webp` | `Assets.v2BgWave.orLight` |

`orLight`（`ThemeStringExt`，`lib/provider/theme_provider.dart`）：暗黑返回路径本身；浅色把**第一个** `.` 换成 `_light.`（即扩展名前插入 `_light`）。常量必须指向**不含** `_light` 的暗黑路径。

## 流程

1. 解析 Figma URL：`fileKey`；`node-id=3827-2981` → `nodeId=3827:2981`。
2. 先盘点本地浅色图（`*_light.*`）和现有 `Assets.*Light` 调用，再对照稿面逐个配对。
3. 调用 `get_design_context` 前加载 `figma-design-to-code`，并在 `skillNames` 里带上它。
4. 用 PIL 读浅色文件：`size` / `mode` / `format`。暗黑导出后必须对齐这三项（差 1px 就 resize）。
5. `download_assets` 只支持 png/jpg/svg/pdf。先按浅色倍率导 PNG（图标通常 **3x**：24→72、26→78、15→45、10→30；390×223 → 1170×669），再转成浅色格式。
6. 下载 MCP 返回的短时 URL（`curl -fsSL`），写入目标路径。禁止手绘 SVG/PNG。
7. 在 `lib/generated/assets.dart` 用 StrReplace 补暗黑常量，紧挨对应 `*Light`；不要整文件覆盖。
8. 所有调用改为 `.orLight`；去掉这些 `MyImage` / `Image.asset` 上的 `const`（`.orLight` 不是编译期常量）。
9. 暗黑资源就绪后，删掉 `if (!themeProvider.isDark)` 这类「只在浅色显示」的包裹。
10. 改完代码后 `graphify update .`。不要 commit。

## 透明底

Figma 整帧导出的 PNG 常带页面底（多为 `#181829`），浅色图标却是 RGBA 透明。若浅色 `mode=RGBA` 且四角透明、暗黑四角不透明：按页面底色抠掉近色像素，保留字形/红点。全幅背景图（如 `bg_wave`）若浅色是不透明 RGB webp，暗黑也转 RGB，不要抠透明。

## 调用注意

- 不要给主题图标加白色 `color:` tint（会盖掉未读红点等彩色）。
- 稿里只有「铃铛+红点」时：导出为 `ic_bell_active`，再去掉红点得到 `ic_bell`。
- 用户头像、空态、Tab 图标：稿面对不上或已有成对资源则跳过，向用户说明。
- `pubspec.yaml` 已按目录声明 assets 时，不必为单张图改 yaml；提醒热重启。

## WebP 转换

```python
from PIL import Image
im = Image.open(src)
if im.size != light.size:
    im = im.resize(light.size, Image.Resampling.LANCZOS)
if light.mode == "RGB":
    im = im.convert("RGB")
im.save(dst, "WEBP", quality=90, method=6)
```
