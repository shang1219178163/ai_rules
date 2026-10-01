---
name: ios-pod-proxy
description: >-
  让 Flutter/iOS 工程的 CocoaPods 安装走本地 HTTP 代理（Clash 等）。在 Podfile
  顶部强制设置 http(s)_proxy，使 pod install / flutter run / flutter build ios
  触发的下载都走代理。Use when 用户说 pod 走代理、CocoaPods 代理、ios pod
  安装代理、pod install 超时/被墙、CDN 下载慢、或要给 Podfile 加代理。
alwaysApply: false
---

# iOS CocoaPods 安装走本地代理

让本工程 `pod install`（含 Flutter 触发的安装）统一走本地代理，避免 CDN / git 直连失败或过慢。

## 何时使用

- 用户要求「pod 走代理」「CocoaPods 代理」
- `pod install` / `flutter build ios` 下载 Specs、git pod、二进制超时或被墙
- 新建或改造 Flutter iOS 工程的 `Podfile`

## 步骤

### 1. 确认代理端口

```bash
networksetup -getwebproxy Wi-Fi
networksetup -getsocksfirewallproxy Wi-Fi
```

取 **Enabled: Yes** 的 `Server` + `Port`。本机 Clash 常见：

| 来源 | 地址 |
|------|------|
| 系统 Wi-Fi 代理（优先） | `http://127.0.0.1:7892` |
| bash_profile 旧默认 | `http://127.0.0.1:7890` |

无系统代理时，问用户端口；不要猜 VPN 品牌专用端口。

### 2. 改 `ios/Podfile` 顶部

放在 `platform` 之后、其它逻辑之前。已有 `*_proxy` 环境变量时优先用环境变量，否则用检测到的默认值：

```ruby
# CocoaPods / git / CDN 下载统一走本地代理（可被 shell 里已有的 *_proxy 覆盖）
_pod_proxy = ENV['https_proxy'] || ENV['HTTPS_PROXY'] || ENV['http_proxy'] || ENV['HTTP_PROXY'] || 'http://127.0.0.1:7892'
ENV['http_proxy']  = _pod_proxy
ENV['https_proxy'] = _pod_proxy
ENV['HTTP_PROXY']  = _pod_proxy
ENV['HTTPS_PROXY'] = _pod_proxy
ENV['all_proxy']   = _pod_proxy
ENV['ALL_PROXY']   = _pod_proxy
ENV['no_proxy']  ||= 'localhost,127.0.0.1,::1'
ENV['NO_PROXY']  ||= ENV['no_proxy']
```

把默认值里的 `7892` 换成步骤 1 的实际端口。

只改 `Podfile` 顶部代理块；不要整文件 Write 覆盖。

### 3. 执行安装

```bash
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
cd ios && pod install
# 或
fvm flutter pub get && fvm flutter build ios --config-only
```

CocoaPods 需要 UTF-8；缺 `LANG` 会出编码警告甚至异常。

### 4. 验证

- `pod install` 日志能拉 Specs / 下载 pod，无长时间卡在 `CDN: trunk Relative path...`
- 临时关掉 Clash 再装应明显变慢或失败（可选）

## 注意

- **优先写 Podfile**：Flutter 子进程不一定继承用户 shell 的 `export http_proxy`；写进 Podfile 才能覆盖 `flutter run` / `flutter build ios`。
- **不要**把代理写进业务 Dart 代码。
- **不要**为「走代理」去改 `source` 成国内镜像，除非用户明确要镜像而不是代理。
- 端口变更：改 Podfile 默认值，或先 `export https_proxy=http://127.0.0.1:<port>` 再装。
- 与 SPM：本工程若关了 Swift Package Manager，仍只靠 CocoaPods；代理块照样有效。

## 检查清单

```
- [ ] 已读系统/用户代理端口
- [ ] Podfile 顶部有 _pod_proxy ENV 块
- [ ] 默认端口与当前代理一致
- [ ] LANG=en_US.UTF-8 下 pod install 成功
```
