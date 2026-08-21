# UI 设计与代码文件清单

> 供设计/前端专家评审优化建议用。项目：「我们的故事」私人共享回忆时间轴。

---

## 一、页面结构总览

```
用户访问
   │
   ▼
登录页 (/login)          ← 密码进入
   │
   ▼
时间轴首页 (/)           ← 核心页面，垂直时间轴
   │
   ├── 新增回忆 Bottom Sheet (弹窗，含照片选择+预览)
   ▼
事件详情页 (/event/<id>)  ← 照片书式浏览
   ├── 上传照片 Bottom Sheet
   └── 全屏 Lightbox
```

---

## 二、设计系统（当前实现）

| 令牌 | 值 | 用途 |
| --- | --- | --- |
| `--color-cream` | `#faf7f2` | 页面底色（暖白） |
| `--color-ink` | `#2b2b2b` | 主文字（近黑） |
| `--color-warm` | `#f6efe6` | 图片占位底 |
| `--color-accent` | `#e8a87c` | 时间轴圆点（暖橙） |

- **大留白**：标题区 `pt-14 pb-10`，卡片间距 `space-y-12`
- **大圆角**：卡片 `rounded-[1.75rem]`，按钮 `rounded-2xl`，弹窗 `rounded-t-[2rem]`
- **柔和阴影**：`.card-shadow`（双层，0 10px 30px + 0 2px 8px）
- **微动画**：登录页渐入/上浮、时间轴卡片交错浮现（`--i` 索引延时）、圆点弹跳、照片淡入
- **字体**：PingFang SC / Noto Sans SC / Microsoft YaHei（中文优先栈）
- **移动优先**：`viewport-fit=cover`、安全区 `env(safe-area-inset-bottom)`、底部操作栏

### 设计参考
Apple Photos · iOS 相册 · Notion Timeline · 小红书收藏页

---

## 三、代码文件清单

### 后端（UI 数据来源）

| 文件 | 作用 |
| --- | --- |
| `app.py` | Flask 入口；注册蓝图、CSRF 全局校验、`date_cn` 模板过滤器 |
| `routes/auth.py` | 登录/登出 |
| `routes/timeline.py` | 时间轴首页（列出事件） |
| `routes/event.py` | 事件详情 / 新增 / 删除 |
| `routes/photo.py` | 照片上传 / 访问（受保护）/ 删除 |
| `models/event.py` | 事件查询（含照片数、封面） |
| `models/photo.py` | 照片记录查询 |

### 前端模板（UI 核心）

| 文件 | 作用 |
| --- | --- |
| `templates/base.html` | 骨架；Flash 消息；`alpine.min.js` + `app.js`（defer，app.js 带 `?v=2`） |
| `templates/login.html` | 登录页（动画：背景渐入→锁→标题→输入框） |
| `templates/timeline.html` | 时间轴首页（竖线+圆点+卡片交错浮现；FAB + 按钮；登出） |
| `templates/event.html` | 事件详情（标题/日期/地点/正文 + 瀑布流 + 底部操作栏 + Lightbox） |
| `templates/partials/add_sheet.html` | 「新增回忆」Bottom Sheet（日期/标题/地点/文字/照片+预览） |
| `templates/partials/upload_sheet.html` | 「上传照片」Bottom Sheet（多选 + 预览网格 + 进度条） |
| `templates/404.html` | 404 页（「这段回忆不存在」） |
| `templates/error.html` | 通用错误页（413 等） |

### 前端样式/脚本

| 文件 | 作用 |
| --- | --- |
| `static/css/input.css` | **设计系统源文件**（Tailwind v4 `@theme` 定义令牌 + 全局样式） |
| `static/css/app.css` | Tailwind 构建产物（**改样式应改 input.css 后 `npm run build:css`**） |
| `static/js/app.js` | 交互脚本（图片多选预览-事件委托 / 上传进度 XHR） |
| `static/js/alpine.min.js` | Alpine.js（当前仅 base.html 加载，页面几乎未使用 Alpine 特性） |
| `static/img/favicon.svg` | 站点图标 |

---

## 四、当前 UI 的关键交互

### 1. 登录页 (`login.html`)
- 全屏居中，暖色渐变背景
- 锁图标 → 标题「我们的故事」→ 副标题 → 密码框 → 「进入」按钮
- 动画：背景 `fadeIn` 1.2s，标题/锁/输入框依次 `floatUp`（0.2s/0.35s/0.55s/0.75s 延时）
- 密码框 `tracking-[0.3em]`（字间距加宽，密码风格）

### 2. 时间轴首页 (`timeline.html`)
- 顶部居中大标题
- 垂直时间轴：中央竖线（PC）/ 左侧竖线（手机），暖橙圆点 + 白环
- 事件卡片：封面图（4:3，hover 缩放 105%）+ 标题 + 日期（YYYY.MM.DD）+ 地点 + 照片数
- 卡片布局 PC 端：**单列**，卡片居右（`md:w-[calc(50%-3rem)] md:ml-auto`），竖线在左中
- 卡片入场：`cardIn`（translateY 28px + 淡入 + 缩放），按 `--i` 索引 0.12s 递增
- 右下角 FAB `+`（微信朋友圈风格），右上角「退出」（POST 表单）
- 空状态：🌱 + 「还没有回忆」

### 3. 事件详情页 (`event.html`)
- 顶部 sticky 返回栏（毛玻璃渐变）+ 标题「回忆详情」
- 事件信息：大标题 / 日期（`2026年8月24日` 中文）/ 地点（带 pin 图标）/ 正文（`whitespace-pre-line`）
- 照片瀑布流：CSS `columns` 多列，2列（手机）/ 3列（PC），`photoIn` 交错淡入
- 点击照片 → 全屏 Lightbox（黑底，居中大图，左右切换按钮，触摸滑动，键盘 ESC/←/→，照片计数）
- 底部固定操作栏：`上传照片`（主按钮）+ `删除回忆`（垃圾图标，confirm 确认）
- Bottom Sheet 上传：多选照片 → 预览网格（3列）→ 进度条 → 完成后 reload

### 4. Bottom Sheet（新增/上传）
- 底部滑入：遮罩 `bg-black/40 backdrop-blur-sm` + 面板 `rounded-t-[2rem] shadow-2xl`
- 顶部拖拽条（`w-10 h-1.5 rounded-full`）
- 移动端 `max-h-[85vh] overflow-y-auto`，底部 `safe-area-inset-bottom`

---

## 五、可优化方向（供专家参考）

### 视觉 / 设计
1. **时间轴布局**：目前 PC 端卡片居右、单列。可考虑「左右交替」（zig-zag）、或卡片内大图更沉浸
2. **封面图比例**：固定 `aspect-[4/3]`，未使用照片的封面显示 📷 占位，可改用最近照片的模糊背景
3. **日期样式**：首页用 `2026.07.19` 紧凑格式，详情页用中文长格式，风格未统一
4. **动效细腻度**：卡片入场有延迟，但 Lightbox 切换、Bottom Sheet 弹入缺少过渡动画（当前是 `classList` 直接切换 `hidden`，无 CSS transition）
5. **主题色**：单一暖橙 accent，可考虑支持暗色模式 / 多主题

### 交互
6. **Bottom Sheet 无过渡**：新增/上传弹窗是「加 hidden class」瞬间出现/消失，无上滑/下滑动画（与「底部滑入」的设计意图不符）
7. **Lightbox 切换**：无缩放/淡入过渡，切换瞬间换图
8. **表单反馈**：新增回忆保存后直接跳详情，无成功提示动画
9. **图片加载**：缩略图 `loading=lazy` 已做，但无骨架屏/占位过渡，大图 loading 时会闪

### 技术
10. **Alpine.js 基本未用**：仅加载未使用，可移除或真正用它做弹窗/状态管理
11. **CSS 构建**：改动样式需 `npm run build:css`，开发时可开 `npm run watch:css`
12. **JS 版本号**：`app.js?v=2` 已加，后续改动需递增版本号避免缓存

---

## 六、核心代码摘录

### 设计系统源 (`static/css/input.css`)
```css
@import "tailwindcss";
@source "../../templates/**/*.html";
@source "../../static/js/**/*.js";

@theme {
  --color-cream: #faf7f2;
  --color-ink: #2b2b2b;
  --color-warm: #f6efe6;
  --color-accent: #e8a87c;
}
html { font-family: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif; }
body { background-color: var(--color-cream); color: var(--color-ink); min-height: 100vh; }
.card-shadow { box-shadow: 0 10px 30px rgba(31,27,22,0.08), 0 2px 8px rgba(31,27,22,0.04); }
.pb-safe { padding-bottom: calc(env(safe-area-inset-bottom,0px) + 1.5rem); }
```

### 时间轴入场动画 (`timeline.html` 内联)
```css
@keyframes cardIn {
  from { opacity: 0; transform: translateY(28px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.timeline-card { opacity: 0; animation: cardIn 0.7s cubic-bezier(0.22,1,0.36,1) forwards; animation-delay: calc(var(--i) * 0.12s); }
```

### 图片预览（事件委托，`static/js/app.js`）
```js
document.addEventListener('change', function (e) {
  const input = e.target;
  if (!(input && input.id === 'add-photos')) return;
  const preview = document.getElementById('add-preview');
  if (!preview) return;
  preview.innerHTML = '';
  Array.from(input.files || []).slice(0, 12).forEach(function (file) {
    const url = URL.createObjectURL(file);
    const div = document.createElement('div');
    div.className = 'relative aspect-square rounded-xl overflow-hidden bg-cream';
    const img = document.createElement('img');
    img.src = url; img.className = 'w-full h-full object-cover';
    div.appendChild(img); preview.appendChild(div);
  });
});
```

### Bottom Sheet 弹层结构 (`add_sheet.html` 精简)
```html
<div id="add-sheet" class="hidden fixed inset-0 z-50">
  <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" onclick="...add('hidden')"></div>
  <div class="absolute bottom-0 inset-x-0 bg-white rounded-t-[2rem] shadow-2xl max-h-[90vh] overflow-y-auto">
    <div class="pt-4 pb-2 flex items-center justify-center"><div class="w-10 h-1.5 rounded-full bg-ink/15"></div></div>
    <h2 class="px-6 text-lg font-semibold text-ink">新增回忆</h2>
    <form method="post" action="{{ url_for('event.new') }}" ...>
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
      <!-- 日期 / 标题 / 地点 / 描述 / 照片 -->
    </form>
  </div>
</div>
```

---

*生成时间：2026-08-21*
