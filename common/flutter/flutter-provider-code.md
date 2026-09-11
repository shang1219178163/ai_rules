---
name: flutter-provider-code
description: >-
  按 provider 包规范编写 Flutter 状态管理代码。触发：涉及 Provider/ChangeNotifierProvider/ProxyProvider/MultiProvider、
  context.watch/read/select、Provider.of 读写、provider 懒加载与生命周期、以及"widget 重 build 太频繁/initState
  读 provider 报错/ChangeNotifier 在 build 期间被改"等 provider 相关的代码书写。专注于"怎么写才正确"，不做架构选型。
alwaysApply: false
---

# Flutter Provider 代码规范

将 `provider` 包的使用约束固化为书写规则，避免常见的生命周期与性能误用。遇到不确定时先看 [provider 官方文档](https://pub.flutter-io.cn/documentation/provider/latest/provider/provider-library.html)。

## 一、暴露一个值（Provider 的三种构造）

| 场景 | 用哪个构造 | 规则 |
|---|---|---|
| 创建并暴露**新对象** | 默认构造（`create`） | ✅ 推荐。对象由 provider 负责创建/监听/销毁 |
| 复用**已存在**的对象实例 | `.value` 构造 | ✅ 推荐。避免 dispose 时对象仍被使用 |
| 创建对象时依赖**会变化的变量** | 默认构造传参与值 | ❌ 不推荐，变量变化对象不更新，改用 `ProxyProvider` |

```dart
// ✅ 推荐：create 里创建新对象
Provider(create: (_) => MyModel(), child: ...)

// ❌ 不推荐：用 .value 创建新对象
ChangeNotifierProvider.value(value: MyModel(), child: ...)

// ❌ 不推荐：用可能随时间改变的变量创建对象
Provider(create: (_) => MyModel(count), child: ...)
```

### 懒加载

`create`/`update` 回调默认**延迟调用**（变量被读取时才执行）；想预先计算则禁用懒加载：

```dart
MyProvider(create: (_) => Something(), lazy: false)
```

## 二、读取值

用 `BuildContext` 扩展方法，向上查找最近的 `T` 类型 provider，**复杂度 O(1)**（不遍历整棵树，找不到抛错）。

- `context.watch<T>()`：监听 `T` 变化，值变则重 build。
- `context.read<T>()`：直接返回 `T`，不监听。**不能在 `StatelessWidget.build` 与 `State.build` 内调用**（其余位置随意）。
- `context.select<T, R>(R cb(T value))`：只监听 `T` 的某一部分，减少重 build。
- `Provider.of<T>(context)`：等同 `watch`；`Provider.of<T>(context, listen: false)` 等同 `read`。

```dart
// 读取并监听可选对象：声明为可空类型，找不到时返回 null 而非抛错
context.watch<Model?>()   // 原本 context.watch<Model>() 找不到会抛 ProviderNotFoundException
```

## 三、MultiProvider

大量注入时避免 `Provider` 多层嵌套，用 `MultiProvider`（仅改书写方式，行为一致）：

```dart
MultiProvider(
  providers: [
    Provider<Something>(create: (_) => Something()),
    Provider<SomethingElse>(create: (_) => SomethingElse()),
    Provider<AnotherThing>(create: (_) => AnotherThing()),
  ],
  child: someWidget,
)
```

## 四、ProxyProvider

将多个 provider 的值聚合为一个新对象，任一依赖更新时**同步更新**该对象。类名数字 = 依赖的 provider 数量；`ChangeNotifierProxyProvider`/`ListenableProxyProvider` 把值传给对应类型的 provider 而非 `Provider`。

```dart
ChangeNotifierProvider(create: (_) => Counter()),
ProxyProvider<Counter, Translations>(
  update: (_, counter, __) => Translations(counter.value),
)
```

## 五、常见坑（务必避开）

1. **`initState` 里调 `watch` 会报错**——因为 `initState` 是永不重调的生命周期，不能监听。
   - 只读一次：改用 `context.read<Foo>().value`（忽略后续更新）。
   - 需监听后续变化：改到 `build` 里，用局部变量对比后再写逻辑。

2. **热重载处理对象**：让对象实现 `ReassembleHandler`，`ChangeNotifierProvider(create: (_) => Example())`。

3. **`ChangeNotifier` 在 widget 树构建期间被改会抛错**——因部分 widget 拿到旧值、部分拿到新值，造成 UI 不一致。把变更放到不受 build 影响的位置：
   - 在 model 构造方法内直接调用：`MyNotifier() { _fetchSomething(); }`
   - 或用 `Future.microtask(() => context.read<MyNotifier>().fetch(someValue));`

4. **widget 重 build 太频繁**：改用 `context.select`，或用 `Consumer`/`Selector` 的 `child` 参数只让子树局部重 build。

```dart
// 只用 watch 整个 Person，name 之外变化也重 build
final person = context.watch<Person>();
return Text(person.name);

// 改为 select 只监听 name
final name = context.select((Person p) => p.name);
return Text(name);
```

5. **相同类型不能同时查两个不同 provider**：widget 只会拿到最近的一个。用泛型区分类型。

```dart
// ❌ 两个 Provider<String>，最近者覆盖
Provider<String>(create: (_) => 'England', child: Provider<String>(...))

// ✅ 用不同类型区分
Provider<Country>(create: (_) => Country('England'), child: Provider<City>(...))
```

6. **消费接口、提供实现**：消费处写接口类型，`create` 里给具体实现，需显式类型提示。`ChangeNotifierProvider<ProviderInterface>(create: (_) => ProviderImplementation(), child: Foo())`。

## 校验清单（写完代码自查）

- [ ] 新对象是否用 `create`（而非 `.value`）？
- [ ] 复用已有对象是否用 `.value`（而非 `create`）？
- [ ] `build` 内是否误用了 `read`？
- [ ] `initState` 是否误用了 `watch`？
- [ ] 变更 notifier 的调用是否可能发生在 build 期间？
- [ ] 是否需要 `select`/`Consumer` 来避免过度重 build？
- [ ] 同类型 provider 是否因未区分泛型而互相覆盖？
