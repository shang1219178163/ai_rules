---
name: codex-reconnect-diagnosis
description: 排查 Codex/Claude Desktop 一直 Reconnecting 或模型请求失败的问题：检测 CC-Switch 本地代理与科学上网代理端口，定位转发链路故障，写入 ~/.codex/.env 代理配置。
alwaysApply: false
---

# Codex / Claude Desktop Reconnecting 排查与修复

## 何时使用
当用户反馈 Codex 或 Claude Desktop 一直显示 "Reconnecting"、模型请求超时、反复 "stream disconnected - retrying"，或者模型完全无响应时使用本 skill。典型场景是用户通过 CC-Switch 等工具切换 DeepSeek/Kimi 等第三方模型，由本地代理转发。

## 核心概念（必须先理解）
- **CC-Switch 本地接管代理**：默认监听 `127.0.0.1:15721`。它改写 Codex/Claude 的 `base_url` 指向自身，再把请求转发到真实上游（如 `https://api.deepseek.com`）。
- **科学上网代理（GlobalProxy）**：CC-Switch 转发上游请求时自身也走一个 HTTP 代理，通常在 `127.0.0.1:7890~7899` 区间（本案例是 7892）。这个代理如果挂了，CC-Switch 转发就会 TLS 握手失败。
- **两层代理关系**：`Codex → CC-Switch(15721) → GlobalProxy(7892) → api.deepseek.com`。任一环节断链都会导致 Reconnecting。
- `~/.codex/.env` 是 **Codex 启动时加载** 的环境变量文件，修改后必须完全重启 Codex 才生效。Claude Desktop 对应的是 shell 里的 `ANTHROPIC_BASE_URL` 等（由 CC-Switch 接管）。

## 排查步骤

### 第 1 步：读取 Codex 配置，确认请求走向
读取 `/Users/shang/.codex/config.toml`：
- 找 `[model_providers.custom]` 下的 `base_url`。若指向 `http://127.0.0.1:15721`，说明被 CC-Switch 接管。
- 记录 `model` 和 `wire_api`。

### 第 2 步：看 Codex 日志，确认错误类型
读取 `/Users/shang/.codex/log/codex-tui.log` 尾部：
- `stream disconnected - retrying sampling request (x/5)` → 流式响应中断，Codex 内部重试，UI 表现为 Reconnecting。
- `unexpected status 502 Bad Gateway ... url: http://127.0.0.1:15721/v1/responses` → 上游转发失败，CC-Switch 返回了 502。

### 第 3 步：看 CC-Switch 日志，定位转发故障
读取 `/Users/shang/.cc-switch/logs/cc-switch.log` 尾部：
- 启动段：`[GlobalProxy] Initialized: http://127.0.0.1:XXXX` —— **这就是实际使用的科学上网代理端口**。
- 转发段：`[SRV-001] 代理服务器启动于 127.0.0.1:15721`。
- 错误段：
  - `TLS handshake failed: Connection reset by peer` / `tls handshake eof` → GlobalProxy 链路不通。
  - `[CB-004] 熔断器触发: 连续失败 N 次 → Open` → 熔断器已打开，后续请求直接快速失败。

### 第 4 步：确认 CC-Switch 代理端口（数据库）
用 Python 读取 `/Users/shang/.cc-switch/cc-switch.db`：
- `proxy_config` 表：`listen_address`/`listen_port`（CC-Switch 监听端口，通常是 15721）、`app_type`。
- `providers` 表：`is_current=1` 的 codex provider，其 `settings_config.config` 里的 `base_url`。
- `settings.json`：`enableLocalProxy`、`currentProviderCodex`。
- 日志中 `[GlobalProxy]` 一行是确定科学上网端口的最可靠来源。

### 第 5 步：测试端口连通性
在沙盒/终端分别测试（注意沙盒内访问不到用户本机 127.0.0.1，只能测到外部代理地址）：
```bash
curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" \
  -x http://127.0.0.1:7892 --connect-timeout 5 https://api.deepseek.com
```
- 返回 401/200 → 代理链路通（401 也代表通，只是缺鉴权）。
- 返回 000/超时 → 代理链路断。

### 第 6 步：检查 ~/.codex/.env 与 sync_proxy_env.sh 是否存在
这两个文件是本方案的核心，**如果缺失，按本 skill 末尾的「文件模板」重建**：
- 缺失则先照模板创建，再进入第 7 步。
- 注意 `~/.codex/sync_proxy_env.sh` 需要 `chmod +x`。
- 重建 `.env` 时端口值先按检测到的最新端口填写，之后脚本会自动接管。

### 第 7 步：写入/核对 ~/.codex/.env
```bash
# 必须同时写 HTTP_PROXY 和 HTTPS_PROXY，指向检测到的科学上网代理端口
HTTP_PROXY=http://127.0.0.1:7892
HTTPS_PROXY=http://127.0.0.1:7892
# 关键：NO_PROXY 必须含 127.0.0.1，否则 Codex 连接本地 CC-Switch(15721) 会被二次转发
NO_PROXY=localhost,127.0.0.1,::1
```
如果 `.env` 已有内容，保留原有行，仅更新代理相关键。**不要**在 `.env` 里写 `ALL_PROXY` 指向本地 CC-Switch 端口（15721），会形成循环。

### 第 8 步：端口变化的自动化（重要）
代理端口一旦变化，手写 `.env` 会失效。自动化方案：

**a) 启动前同步（zshrc 包装函数）**
`~/.codex/sync_proxy_env.sh` 检测 macOS 系统代理端口（`scutil --proxy` 读 HTTPEnable/HTTPPort），端口变化则原子重写 `.env`。在 `~/.zshrc` 定义同名函数包裹真正的 codex：
```zsh
codex() {
  ~/.codex/sync_proxy_env.sh
  if [ -f "$HOME/.codex/.env" ]; then set -a; . "$HOME/.codex/.env"; set +a; fi
  command codex "$@"
}
```

**b) Codex 生命周期 hook（会话内提醒）**
Codex 原生支持 hooks，**配置在 `config.toml` 的 `[hooks]` 段**（不是独立 hooks.toml 文件！）。`SessionStart` 事件在会话创建时触发。已配置：
```toml
[hooks.SessionStart]
hooks = [
  { type = "command", command = "~/.codex/sync_proxy_env.sh --check", timeout = 5 },
]
```
`sync_proxy_env.sh --check` 检测模式：端口相同则静默；端口变化则重写 `.env` 并输出 `⚠ 代理端口发生改变 （旧 —> 新），请重启客户端。`，由 Codex 展示在界面。hook 命令经 `$SHELL`（`/bin/sh -lc`）执行，`~` 会正常展开。
**注意**：hook 在进程启动后才触发，改 `.env` 对当前进程无效，因此只能提醒，真正生效仍需重启客户端。hook 是诊断/提醒，zshrc 包装是自动同步，两者互补。

### 第 9 步：验证与告知
- 重新读取 `.env` 确认内容正确。
- 告知用户：**必须完全退出 Codex 再重新打开**，`.env` 在启动时加载。
- 若重启后仍 Reconnecting，说明问题在科学上网代理本身（节点挂了），引导用户：
  1. 打开代理工具确认 7892 对应节点开启且可用；
  2. 若代理端口变了，同步改 `.env`（或依赖上述自动化）；
  3. 换 DeepSeek 可用节点。

## 关键判断表
| 现象 | 结论 | 处理 |
|---|---|---|
| Codex 日志 `stream disconnected - retrying` | 流式响应中断 | 查 CC-Switch 转发链路 |
| CC-Switch 日志 TLS handshake failed | 科学上网代理(GlobalProxy)不通 | 修代理工具/换节点 |
| CC-Switch 日志 熔断器 Open | 连续失败触发熔断 | 修上游后需等待熔断恢复（约 60~90s） |
| 端口测试 401 | 链路通 | 配置正确，只需重启 Codex |
| 端口测试 000/超时 | 链路断 | 修代理工具，勿只改 .env |

## 文件模板（文件缺失时据此重建）

### 模板 1：`~/.codex/sync_proxy_env.sh`
创建后执行 `chmod +x ~/.codex/sync_proxy_env.sh`。

```bash
#!/usr/bin/env bash
# ==============================================================================
# Codex 代理端口自动同步/检测脚本
# ------------------------------------------------------------------------------
# 作用：检测 macOS 系统代理端口，并同步到 ~/.codex/.env。
#
# 检测来源：macOS 系统代理设置（scutil --proxy 读取 SystemConfiguration）。
#           适用于 ClashX / Clash Verge / Surge 等开启"系统代理"的工具。
#
# 两种模式：
#   （默认，同步模式） 启动 Codex 前调用：端口变化则更新 .env
#       ~/.codex/sync_proxy_env.sh
#
#   （--check，检测模式） Codex SessionStart hook 调用：端口相同则静默；
#       端口变化则重写 .env 并输出"请重启客户端"提醒（供 hook 展示）
#       ~/.codex/sync_proxy_env.sh --check
#
# 退出码：
#   0  正常（端口一致；或已同步）
#   2  系统代理未开启（保留 .env 原值）
#   3  非 macOS（无 scutil，跳过）
# ==============================================================================

set -u

ENV_FILE="${CODEX_ENV_FILE:-$HOME/.codex/.env}"
LOCK_FILE="$HOME/.codex/.sync_proxy_env.lock"
CHECK_MODE=0
[ "${1:-}" = "--check" ] && CHECK_MODE=1

# 颜色（tty 下才启用，非交互输出保持干净）
if [ -t 1 ]; then
  C_INFO=$'\033[36m'; C_OK=$'\033[32m'; C_WARN=$'\033[33m'; C_END=$'\033[0m'
else
  C_INFO=''; C_OK=''; C_WARN=''; C_END=''
fi

info()  { printf '%s[sync-proxy] %s%s\n' "$C_INFO" "$*" "$C_END"; }
ok()    { printf '%s[sync-proxy] %s%s\n' "$C_OK" "$*" "$C_END"; }
warn()  { printf '%s[sync-proxy] %s%s\n' "$C_WARN" "$*" "$C_END" >&2; }

# 从 .env 读取当前已写入的代理端口（无则返回空）
read_current_port() {
  [ -f "$ENV_FILE" ] || return 0
  grep -E '^HTTPS_PROXY=http://127\.0\.0\.1:[0-9]+$' "$ENV_FILE" \
    | head -1 | sed -E 's|^HTTPS_PROXY=http://127\.0\.0\.1:([0-9]+)$|\1|'
}

# 不是 macOS（没有 scutil）时跳过，退出码 3
if ! command -v scutil >/dev/null 2>&1; then
  warn "当前系统无 scutil（非 macOS），跳过代理端口自动同步"
  exit 3
fi

# 加锁，避免多个终端并发启动 Codex 时同时改写 .env
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  [ "$CHECK_MODE" = "1" ] || warn "已有另一个同步进程在运行，跳过本次同步"
  exit 0
fi

# 解析系统代理：只有 HTTPEnable=1 且 HttpPort 有效时才视为已开启
enable="$(scutil --proxy | awk -F' *: *' '/HTTPEnable/{print $2}')"
port="$(scutil --proxy | awk -F' *: *' '/HTTPPort/{print $2}')"

if [ "$enable" != "1" ] || ! [[ "$port" =~ ^[0-9]+$ ]]; then
  [ "$CHECK_MODE" = "1" ] || warn "系统代理未开启或未读到 HTTP 代理端口，保留 .env 原值"
  exit 2
fi

current_port="$(read_current_port)"

# 端口无变化：静默退出（两种模式一致）
if [ -n "$current_port" ] && [ "$current_port" = "$port" ]; then
  exit 0
fi

# 端口有变化：重写 .env
tmp_file="$ENV_FILE.tmp"
umask 077
{
  printf '# Codex 网络代理配置\n'
  printf '# 每次启动 Codex 前由 ~/.codex/sync_proxy_env.sh 自动同步系统代理端口\n'
  printf 'HTTP_PROXY=http://127.0.0.1:%s\n' "$port"
  printf 'HTTPS_PROXY=http://127.0.0.1:%s\n' "$port"
  printf '# 本机地址不走代理，避免 Codex 连接本地 CC-Switch 代理(127.0.0.1:15721)时被二次转发\n'
  printf 'NO_PROXY=localhost,127.0.0.1,::1\n'
} > "$tmp_file"

# 原子替换
mv "$tmp_file" "$ENV_FILE"

if [ "$CHECK_MODE" = "1" ]; then
  # 检测模式：向 stdout 输出提醒（Codex hook 会将其展示给用户）
  if [ -n "$current_port" ]; then
    printf '⚠ 代理端口发生改变 （%s —> %s），请重启客户端。\n' "$current_port" "$port"
  else
    printf '⚠ 代理端口已更新为 %s，请重启客户端。\n' "$port"
  fi
else
  ok "已同步代理端口到 $ENV_FILE (HTTP_PROXY/HTTPS_PROXY=http://127.0.0.1:${port})"
fi
exit 0
```

### 模板 2：`~/.codex/.env`
端口值按当前检测到的最新系统代理端口填写（默认 7892），之后由脚本自动接管更新。

```bash
# Codex 网络代理配置
# 自动检测本机正在使用的代理端口并写入（CC-Switch GlobalProxy: 127.0.0.1:7892）
HTTP_PROXY=http://127.0.0.1:7892
HTTPS_PROXY=http://127.0.0.1:7892
# 本机地址不走代理，避免 Codex 连接本地 CC-Switch 代理(127.0.0.1:15721)时被二次转发
NO_PROXY=localhost,127.0.0.1,::1
```

### 重建后必须做的验证
```bash
# 1. 脚本语法与权限
bash -n ~/.codex/sync_proxy_env.sh && chmod +x ~/.codex/sync_proxy_env.sh
# 2. 同步模式试运行（确认能读到系统代理并写入 .env）
~/.codex/sync_proxy_env.sh
# 3. --check 模式试运行（端口一致应静默）
~/.codex/sync_proxy_env.sh --check
# 4. 确认 config.toml 里 hooks.SessionStart 仍在（若 config.toml 也丢失则补配）
grep -A3 'hooks.SessionStart' ~/.codex/config.toml
```

## 注意事项
- 本机端口（15721、7892）在沙盒 Linux 环境里不可达，连通性测试只能用代理工具所在宿主能访问的地址；判断链路靠 CC-Switch 日志 + 外部代理测试。
- 涉及 API key 的字段（`auth.json`、数据库 `settings_config` 中的 token）不要完整输出，做脱敏（前 8 后 4）。
- 不要在未确认端口的情况下盲目写 `.env`；GlobalProxy 端口以 CC-Switch 日志为准。
- Codex hooks 事件有 11 种：SessionStart/SessionEnd/UserPromptSubmit/PreToolUse/PostToolUse/PermissionRequest/PreCompact/PostCompact/SubagentStart/SubagentStop/Stop。handler 类型：command/mcp_tool/prompt/agent。
- hook 的 `command` 支持 `~`（经 `/bin/sh -lc` 执行）。
