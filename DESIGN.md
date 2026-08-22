# 我们的故事 · UI 设计系统文档

## 一、设计理念

| 维度 | 方向 |
|------|------|
| 风格 | 拍立得 / 手账拼贴风 |
| 底色 | 暖奶油 `#fdfbf7` |
| 强调色 | 陶土橘 `#d97d54`，焦糖棕 `#c86d51` |
| 卡片 | 拍立得纸白 `#fcfaf6`，微旋转，上浮 hover |
| 字体 | 标题衬线 `Songti SC`，正文手写 `Kaiti SC`，UI 无衬线 `PingFang SC` |
| 圆角 | 大圆角（2xl / 2.5rem） |
| 阴影 | 细腻弥散阴影，避免硬边 |
| 留白 | 大留白，手机 `px-4`，桌面 `max-w-4xl` |
| 动效 | 入场渐显、Bottom Sheet 上滑、Lightbox 缩放入场、卡片 hover 上浮、节点圆点呼吸光晕 |

---

## 二、色彩设计令牌

```css
--color-cream:      #fdfbf7   /* 页面底色 */
--color-cream-deep: #f8f5ee   /* 输入框 / 卡片底色 */
--color-warm:       #f6efe6   /* 封面占位底色 */
--color-ink:        #2b2b2b   /* 主文字 */
--color-ink-soft:   #57534e   /* 次要文字 */
--color-ink-mute:   #a8a29e   /* 提示 / 弱文字 */
--color-accent:     #d97d54   /* 陶土橘：按钮、圆点、强调 */
--color-accent-soft:#c86d51   /* 焦糖棕：hover 状态 */
--color-paper:      #fcfaf6   /* 拍立得卡片白 */
```

---

## 三、字体系统

```css
--font-serif: "Songti SC", "Noto Serif SC", "STSong", serif;
--font-hand:  "Kaiti SC", "STKaiti", "KaiTi", serif;
```

| 用途 | 字体 | 实例 |
|------|------|------|
| 页面标题 | `font-serif` | 「我们的故事」 |
| 卡片标题 | `font-serif` | 事件名 |
| 手账副标题 | `font-hand` | 「一起走过的日子」 |
| 日期 | `font-hand` | `08.21` |
| 正文 | `font-hand` | 回忆描述 |
| UI 元素 | 系统字体 | 按钮、标签、输入框 |

---

## 四、通用组件

### 4.1 拍立得卡片 `.polaroid`

```css
background: var(--color-paper);
border: 1px solid rgba(43,30,22,0.04);
box-shadow: 多层柔软阴影;
/* 奇数左旋 -0.8°，偶数右旋 0.8° */
/* hover: 上浮 6px + 放大 1.02 + 归正 0° */
transition: 0.45s cubic-bezier(0.22,1,0.36,1);
```

### 4.2 图片框架 `.img-frame`

```css
padding: 6px;
background: var(--color-paper);
/* 内嵌图片圆角 0.9rem */
```

### 4.3 阴影

```css
.card-shadow     /* 轻量漂浮 */
.card-shadow-lg  /* 大卡片悬浮 */
```

### 4.4 安全区

```css
.pb-safe  /* 底部 safe-area + 1.5rem */
```

---

## 五、页面详细设计

### 5.1 登录页

| 项目 | 实现 |
|------|------|
| 布局 | 全屏居中，max-w-sm |
| 背景 | 暖色渐变：`#fdf6ec → #f7efe6 → #f3e7da` |
| 锁图标 | 白底毛玻璃大圆角方块，内嵌 SVG 锁 |
| 标题 | 衬线 4xl，「我们的故事」 |
| 副标题 | 「记录我们一起经历的时光」 |
| 密码框 | 白底毛玻璃大圆角，文字居中，密码遮蔽 |
| 按钮 | 纯黑圆角按钮，带阴影 |
| 动画 | 背景淡入 → 锁浮起 → 标题浮起 → 输入框浮起，逐级延迟（0.2s/0.35s/0.55s） |
| 脚注 | 「只有我们知道这里的密码」 |

### 5.2 时间轴首页

| 项目 | 实现 |
|------|------|
| 布局 | 桌面 `max-w-4xl` 居中，手机 `px-4` |
| 页头 | 衬线大标题 + 手写副标题「一起走过的日子」+ 线装饰 |
| 计数器 | 「已一起走过 **N** 天 · M 条回忆」（楷体，陶土橘色） |
| 中轴线 | 竖线渐变 `transparent → #a8a29e 35% → #a8a29e 35% → transparent`，桌面居中、手机 `left:7px` |
| 小太阳 | `position:fixed` 22px 圆点，陶土橘渐变，三层光晕，随滚动吸附到视口中间最近的节点圆点，CSS transition 0.5s 平滑滑动 |
| 节点圆点 | 16px 陶土橘，上方 4px 奶油色环，hover 触发呼吸光晕 |
| Zig-Zag | 奇左偶右，桌面 `flex-row` / `flex-row-reverse`，卡片 `w-[calc(50%-2.5rem)]` |
| 手机 | 单列全宽，卡片 `pl-8`（给轴线留空间） |
| 月份锚点 | sticky `top:1rem`，桌面右列、手机居中，毛玻璃圆角胶囊 |
| 卡片 | 拍立得 `.polaroid` + 微旋转 + 圆角 2xl + padding 4/5 |
| 封面 | 封面包在 `.img-frame` 内，奇数 `aspect-[16/10]` 横构图，偶数 `aspect-[4/5]` 近方竖构图，节奏交替 |
| 封面叠加 | 1 张：单图满铺；2 张：右下角 42% 宽第二张贴纸（`rotate-3` + 白边 + 阴影）；3 张：再加一层 34% 宽第三张（`-rotate-4`） |
| 照片角标 | 半透明玻璃胶囊「N P」在封面右下角 |
| 卡片信息 | 衬线标题 + 手写月日 + 地点（SVG 定位图标） |
| 入场动画 | `IntersectionObserver`，卡片从 `translateY(28px) + opacity:0` 渐入，0.7s 缓出 |
| 空状态 | 🌱 大图标 + 「还没有回忆，点击右下角 + 开始记录」 |
| FAB | 右下角固定 56px 纯黑圆按钮，+ 图标，阴影 |
| 退出 | 左上角固定毛玻璃胶囊按钮 |
| 新增弹层 | Bottom Sheet，Alpine `x-show="openAdd"`，详见 5.4 |

### 5.3 事件详情页

| 项目 | 实现 |
|------|------|
| 导航 | sticky 毛玻璃顶栏，左返回箭头 + 中「回忆详情」+ 右占位 |
| 标题 | 衬线 3xl 居中 |
| 日期 | 手写「2026年8月21日」中文格式 |
| 地点 | 陶土橘底色胶囊，SVG 定位图标 |
| 正文 | 15px 手写体，`whitespace-pre-line` |
| 照片 | CSS columns 瀑布流，手机 2 列、桌面 3 列，每张拍立得卡片 + 微旋转，`animation-delay` 逐张入 |
| 底部栏 | 毛玻璃固定底栏，左「上传照片」陶土橘大按钮 + 右删除 icon 按钮 |
| Lightbox | 全屏黑底 `z-60`，图片缩放淡入 `lb-enter` 动画，左右切换按钮 + 触摸滑动 + 键盘 ESC/方向键，左上角「N / M」计数器 |
| 上传弹层 | Bottom Sheet，Alpine `x-show="openUpload"`，详见 5.5 |

### 5.4 新增回忆 Bottom Sheet

| 项目 | 实现 |
|------|------|
| 结构 | 外层 `fixed inset-0 z-50`，遮罩 `bg-stone-900/40 backdrop-blur-sm`，面板 `absolute bottom-0` 大圆角 2.5rem |
| 动画 | 面板 `translate-y-full → translate-y-0` 400ms 缓出进入，250ms 缓入退出 |
| 遮罩 | 点击关闭（`@click="openAdd = false"`） |
| 拖拽条 | 顶部灰色小横条 |
| 表单 | 日期（input date）、标题（必填）、地点、描述（textarea）、照片（多选 + 预览网格 3 列）、提交按钮 |
| 照片预览 | 事件委托 `data-preview-target`，`URL.createObjectURL` 生成 Blob 缩略 |
| 按钮 | 陶土橘大按钮「保存回忆」，带阴影 |
| 安全区 | `padding-bottom: env(safe-area-inset-bottom)` |

### 5.5 上传照片 Bottom Sheet

| 项目 | 实现 |
|------|------|
| 结构 | 与新增弹层相同（id=`upload-sheet`） |
| 表单 | 照片多选 + 预览网格 + 进度条 + 上传按钮 |
| 上传 | XHR 异步，`FormData`，进度条实时更新百分比，完成后 `location.reload()` |
| 防重 | `e.preventDefault()` 阻止原生提交 |
| 选择区 | 虚线边框 + 📷 图标，hover 变陶土橘边框 |

### 5.6 错误页面

| 页面 | 内容 |
|------|------|
| 404 | 「这段回忆不存在」 |
| 413 | 「文件过大，单张不能超过 15MB」 |
| 通用 | 错误码 + 错误信息 |

---

## 六、交互细节

### 6.1 动画

| 动画 | 实现 | 时长 |
|------|------|------|
| 登录页入场 | CSS `@keyframes` 逐级浮起 | 0.9s |
| 卡片入场 | `IntersectionObserver` + CSS transition | 0.7s |
| 卡片 hover | `transform` 上浮 + 放大 + 归正 | 0.45s |
| 节点圆点 hover | `::after` 径向光晕 opacity 切换 | 0.3s |
| 小太阳滑动 | CSS transition `top`/`left` | 0.5s |
| Bottom Sheet 进入 | `translateY` 上滑 | 0.4s |
| Bottom Sheet 退出 | `translateY` 下滑 | 0.25s |
| Lightbox 进入 | `scale(0.96) → scale(1)` + opacity | 0.25s |
| 瀑布流照片 | `translateY(16px) → 0` + opacity，逐张 0.06s 延迟 | 0.6s |

### 6.2 无障碍

| 措施 | 位置 |
|------|------|
| `prefers-reduced-motion` | 小太阳动画关闭 |
| `aria-hidden="true"` | 小太阳装饰元素 |
| 语义化 HTML | 标题 `h1`/`h2`，导航 `nav`，表单 `label` |
| `loading="lazy"` | 所有图片 |
| `alt` | 所有图片带描述 |

### 6.3 响应式

| 断点 | 行为 |
|------|------|
| 默认（手机） | 单列全宽，轴线在左 7px，太阳在左 |
| `md`（768px+） | Zig-Zag 双列，轴线居中，卡片 50% 宽，月份锚点右列，瀑布流 3 列 |

---

## 七、文件清单

```
static/css/input.css          # 设计令牌 + 全局组件样式（Tailwind v4）
static/css/app.css            # 构建产物（minified）
static/js/app.js              # 图片预览、IntersectionObserver、小太阳、上传
static/js/alpine.min.js       # Alpine.js（轻量交互框架）
static/img/favicon.svg        # 网站图标

templates/base.html           # 骨架：meta、viewport-fit、Alpine、Flash 消息
templates/login.html          # 登录页
templates/timeline.html       # 时间轴首页
templates/event.html          # 事件详情页
templates/partials/add_sheet.html     # 新增 Bottom Sheet
templates/partials/upload_sheet.html  # 上传 Bottom Sheet
templates/404.html            # 404
templates/error.html          # 通用错误
```

---

## 八、技术栈

| 层 | 技术 |
|------|------|
| 后端 | Python Flask + Jinja2 服务端渲染 |
| 数据库 | SQLite |
| CSS | Tailwind CSS v4 + 自定义 `@theme` 令牌 |
| JS | 原生 JS + Alpine.js |
| 图片 | Pillow → WebP（全尺寸 1920 + 缩略图 600） |
| 安全 | Flask Session + CSRF Token + 照片路由保护 |

---

## 九、已知交互状态

| 状态 | 处理 |
|------|------|
| 空时间轴 | 🌱 大图标 + 引导文案 |
| 无照片事件 | 📷 半透明占位 icon |
| 无照片详情 | 🖼️ 大图标 + 「还没有照片」 |
| 上传中 | 进度条 + 百分比 + 按钮禁用 |
| 上传失败 | 「上传失败」/「网络错误」+ 按钮恢复「重试」 |
| 表单验证 | 标题必填、日期必填，后端校验 |
| 密码错误 | Flash 消息「密码不对，再想想？」 |
| 未登录 | 重定向到登录页 |
| CSRF 无效 | 400 Bad Request |