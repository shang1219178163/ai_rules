---
name: flutter-tech-blog
description: 技术博客撰写规范（Flutter/Dart、Swift/SwiftUI 等各技术栈通用）。基于项目真实源码撰写技术博客（发布到掘金等平台），输出 .md 源文 + HTML 预览页，统一存到 ~/Documents/doc 并在项目内建 .blogs 快捷链接。撰写、精简或调整技术博客时使用。
alwaysApply: false
---

# 技术博客撰写规范

在项目内为某个组件/类撰写技术博客（发布到掘金等平台）时，遵循本规范。适用于 Flutter/Dart、Swift/SwiftUI 等各技术栈，标题与关键词按实际技术栈填写。通用原则见 `common/core.md`，此处不重复。

## 核心流程

1. 在项目中搜索用户指定的组件/类名（Grep / Glob，必要时用 `find` 找变体），定位真实源码。
2. 阅读源码 + 相关使用场景：demo 页、mixin、调试页、数据模型、调用处。
3. 按下方固定四节结构撰写。
4. 输出两份文件：`.md` 源文 + 同名 HTML 预览页，保存到**文档目录下的 `doc` 文件夹**（即 `~/Documents/doc/`，跨项目汇总，目录不存在则先创建）。
5. 在**当前项目根目录**建立/确认快捷链接 `.blogs` 指向该目录（见下方「项目内快捷链接」），保证本次会话与后续会话都能直接查看。
6. 再用 `present_files` 分享给用户。
7. **完成后进行一次精简**：主动压缩冗余代码块与说明文字，保留核心机制、踩坑点、总结价值，再交付。通常第一版就该给精简版。

## 文件规范

- 保存位置：**文档目录下的 `doc` 文件夹**，即 `~/Documents/doc/`。所有项目、所有技术栈的博客统一汇总到这里，不保存到项目内的 `doc/`。目录不存在时先 `mkdir -p ~/Documents/doc`。
- 命名：`<项目前缀>_<snake_case_组件名>.md` 与 `<项目前缀>_<snake_case_组件名>_blog_preview.html`。因为是跨项目汇总，文件名需自带辨识度，**项目前缀必填**（如 `flutter_`、`swift_`），避免不同项目的同名组件相互覆盖。
- **项目内快捷链接（必做）**：博客存到 `~/Documents/doc/` 后，在项目里看不到。因此在**项目根目录**建一个指向它的符号链接，让当次会话和后续会话都能直接读取、IDE 里也能直接打开：
  ```bash
  # 项目根目录执行；已存在则跳过，勿覆盖
  [ -e .blogs ] || ln -s ~/Documents/doc .blogs
  ```
  之后统一用 **`.blogs/<文件名>`** 这个项目内路径引用博客（如 `.blogs/swift_navigator.md`），不要用绝对路径 `~/Documents/doc/...`。
  - 建链接后**必须**把 `.blogs` 写进项目 `.gitignore`，避免把指向个人文档目录的链接提交进仓库。
  - 若项目已有同名 `.blogs`，先确认它指向哪里，不要直接覆盖。
  - 该链接是隐藏目录，IDE 需开启「显示隐藏文件」才能看到；`.blogs/blog/` 之类的子目录形式不采用，保持路径统一。
- HTML 预览页：自包含单文件、内联 CSS，掘金排版风格（深色代码块、蓝色左侧标题条、卡片式容器），移动端自适应。**不要引用任何本地相对资源**（外链 css/js/图片），否则文件迁移后无法渲染。
  - **默认深色模式**：`<html>` 标签上直接写死 `data-theme="dark"`，首屏即为深色（不能只靠 JS 设置，否则会先闪一下浅色）。点击标题可切到浅色。
  - **深浅主题切换（必做）**：点击页面顶部标题（`h1`）切换深浅主题。用 CSS 变量 + `data-theme` 属性实现，见下方「主题切换实现」。记住用户选择（`localStorage`）—— 有记录时以记录为准，无记录时用默认深色。

## 主题切换实现

用 CSS 变量定义两套配色，`<html data-theme="dark">` 切换。**默认深色**：`data-theme` 直接写在 `<html>` 标签上，由 HTML 解析阶段就生效，避免 JS 执行前的浅色闪烁。以下为实现骨架，按需调整色值，**保持变量名一致**便于跨文章统一。

**1. `<html>` 标签带默认值**

```html
<html lang="zh-CN" data-theme="dark">
```

**2. 变量与深色覆盖**

```css
:root {
  --brand: #1e80ff;
  --text: #252933;
  --text-2: #4e5969;
  --bg: #f4f5f5;
  --card: #ffffff;
  --code-bg: #282c34;      /* 代码块在两套主题下都保持深色 */
  --code-text: #abb2bf;
  --border: #e5e6eb;
  --inline-bg: #f2f3f5;
  --inline-text: #e64a19;
}

[data-theme="dark"] {
  --text: #e8e8e8;
  --text-2: #a9a9a9;
  --bg: #17181a;
  --card: #232427;
  --border: #35363a;
  --inline-bg: #35363a;
  --inline-text: #ff8a65;   /* 深色下提亮，保证对比度 */
}
```

所有颜色一律通过 `var(--x)` 引用，**不要在规则里写死色值**，否则深色模式会漏改。

**3. 标题可点击的提示**

```css
h1 {
  cursor: pointer;
  user-select: none;
  transition: opacity .15s;
}
h1:hover { opacity: .7; }                      /* 暗示可点击 */
h1::after {                                     /* 主题图标，跟随主题变化 */
  content: "☀️";
  font-size: 18px;
  margin-left: 10px;
  opacity: .55;
  vertical-align: middle;
}
[data-theme="light"] h1::after { content: "🌙"; }
```

**4. 切换脚本（放 `</body>` 前）**

```html
<script>
(function () {
  var root = document.documentElement;
  var KEY = 'blog-theme';

  // 默认深色（已在 <html> 上）；仅当用户切换过时才覆盖
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved === 'light' || saved === 'dark') {
    root.setAttribute('data-theme', saved);
  }

  var h1 = document.querySelector('h1');
  if (!h1) return;
  h1.setAttribute('role', 'button');
  h1.setAttribute('tabindex', '0');
  h1.title = '点击切换深浅主题';

  function toggle() {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(KEY, next); } catch (e) {}
  }

  h1.addEventListener('click', toggle);
  h1.addEventListener('keydown', function (e) {   // 键盘可达
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
  });
})();
</script>
```

**要点**：`data-theme="dark"` 写在 `<html>` 标签上，HTML 解析阶段即生效，**首屏无浅色闪烁**；JS 只在用户切换过后才覆盖它。`localStorage` 包在 `try/catch` 里（`file://` 或隐私模式下可能抛错）；挂 `keydown` 让键盘也能切换。

**5. 交付前自检**

- **打开页面即深色**，不出现先亮后暗的闪烁
- 切换后**代码块**仍清晰可读（深色底 + 浅字，两套主题一致）
- 行内 `code` 的强调色在深色下不刺眼（用 `--inline-text` 单独控制）
- 移动端切换正常，标题换行时图标不错位

## 文章结构（四节固定）

标题格式：`<技术栈> 进阶 | 最佳实践：<一句话卖点>`（卖点体现组件解决的核心问题）。技术栈按实际填写，如 `Flutter`、`Swift`、`SwiftUI`。

首行标题后紧跟一行：`> 关键词：<技术栈>、<组件相关术语>、...`（逗号分隔）。

### 一、需求来源

- 开头一句痛点，加粗：**「开发 XX 时遇到一个痛点：<问题描述>。」**
- 展示原生/传统写法的问题代码 + 编号痛点列表（3 条左右）。
- 结尾一句「需求很朴素：**<组件要解决的诉求>。**」

### 二、使用示例

- 从组件最常用方式开始（推荐方式优先，标注「推荐」）。
- 覆盖：基础用法、变体/显式创建、集成到业务组件。
- 以代码块为主，配简短说明；代码可直接复制使用。

### 三、源码讲解

- 按代码模块拆分为多个 `###` 小节，逐层拆解。
- 每小节：要点标题 + 核心代码 + 关键细节说明。
- 主动标注「关键坑」「易忽略的细节」（如防泄漏、循环引用、脏数据、二次校验等）。

### 四、总结

- 开头一句话点明组件本质：**「<组件> 做的事很朴素：<核心机制>。」**
- 「核心价值：」编号列表（4-5 条，每条 加粗关键词 + 冒号 + 说明）。
- 结尾用 **加粗**（或 blockquote）一句话总结。

## 内容要点

- 全程中文。
- 代码从真实源码提炼，但可精简（构造函数可省略参数、注释压成行内），确保可直接复制使用。
- 保留核心实现与踩坑经验，避免冗余铺垫。
- 引用项目内真实文件路径/组件名，不要杜撰 API。

## 后续迭代（常见用户要求）

- **精简**：压缩冗余代码块与说明文字，保留核心机制、踩坑点、总结价值（见核心流程第 5 条，首版即应精简）。
- **结构微调**：如「第一节标题移到关键字正下方」「使用示例紧跟第一节」——注意用户要求的具体顺序，按需调整。
- 用户可能逐次调整，保持两份文件（md + html）内容始终同步。
