---
name: uipageviewcontroller-container
description: iOS 用 UIPageViewController 横向滚动分页集成一批控制器页面（如 AnimationHomeController 集成 AnimationController1~18）。触发：需要把多个 UIViewController 页面用横向滑动分页集成到一个容器、创建 XxxHomeController 分页容器、UIPageViewController 集成子控制器页面。
alwaysApply: false
---

# UIPageViewController 横向分页集成多个控制器页面

当项目里有一批以共同前缀命名的控制器（如 `AnimationController1` ~ `AnimationController18`）需要在一个页面里横向滑动浏览时，创建一个 `XxxHomeController`（`UIPageViewController` 子类）作为容器，子页面代码保留在各自类中不动。

## 步骤

1. **创建容器控制器**：继承 `UIPageViewController`，在 `init` 中指定 `transitionStyle: UIPageViewControllerTransitionStyleScroll` + `navigationOrientation: UIPageViewControllerNavigationOrientationHorizontal`（横向滚动）。
2. **列出子控制器**：`init` 中维护 `NSArray<NSString *> *vcNames`，按展示顺序列出子控制器类名。
3. **动态实例化**：`viewDidLoad` 中用 `NSClassFromString(name)` 逐个 `[[cls alloc] init]` 生成实例数组；类不存在则 `continue` 跳过。给每个子页设置 `title` 便于导航栏展示。
4. **设置首屏**：`setViewControllers:@[子页.firstObject] direction:Forward animated:NO`。
5. **实现 DataSource**：`viewControllerBefore/AfterViewController:` 用 `[ctlrs indexOfObject:]` 定位相邻页，越界返回 `nil`。
6. **导航栏标题**：delegate `didFinishAnimating:transitionCompleted:` 中，翻页完成后用 `updateTitleForViewController:` 把 `self.title` 设为 `"当前索引/总数 + 子页标题"`。首屏标题在 `viewDidAppear` 中设置（子页 `viewDidLoad` 会覆盖 `navigationItem.title`，需延迟到页面加载完成后取最终标题）。
7. **路由列表只保留容器**：如果项目总览页用运行时扫描展示控制器列表，把 `XxxHomeController` 之外的前缀子页从列表排除（如 `[name hasPrefix:@"AnimationController"]` 跳过），列表只显示容器入口，进入容器后横向滑动浏览全部子页。

## 关键代码

```objc
// 容器 init
- (instancetype)init{
    self = [super initWithTransitionStyle:UIPageViewControllerTransitionStyleScroll
                    navigationOrientation:UIPageViewControllerNavigationOrientationHorizontal
                                  options:nil];
    if (self) {
        self.vcNames = @[@"XxxController1", @"XxxController2", ...];
    }
    return self;
}

// 标题更新
- (void)updateTitleForViewController:(UIViewController *)vc{
    NSInteger idx = [self.ctlrs indexOfObject:vc];
    if (idx == NSNotFound) return;
    NSString *vcTitle = vc.navigationItem.title ?: vc.title ?: NSStringFromClass(vc.class);
    self.title = [NSString stringWithFormat:@"%ld/%ld %@", (long)(idx + 1), (long)self.ctlrs.count, vcTitle];
}
```

## 注意

- 子页面**代码保持在原类中**，容器只做展示编排，不复制业务代码。
- `viewControllerBefore/After` 必须返回 `nil` 表示边界，否则分页会出现无限循环。
- 新增子控制器时只改 `vcNames` 数组，容器逻辑不变。
- 手动 Xcode 工程新增文件要同步注册 `project.pbxproj`（PBXBuildFile、PBXFileReference、group children、Sources 编译项共 4 处）。
