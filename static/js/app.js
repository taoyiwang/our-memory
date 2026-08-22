// 我们的故事 —— 全局交互

// 图片多选预览（事件委托，不依赖 DOMContentLoaded 时序）
document.addEventListener('change', function (e) {
  const input = e.target;
  if (!input || !input.matches('input[type="file"][multiple][data-preview-target]')) return;

  const preview = document.querySelector(input.dataset.previewTarget);
  if (!preview) return;

  // 释放上一次选择产生的 Blob URL，避免反复选择时累积内存
  preview.querySelectorAll('img[data-preview-url]').forEach(function (img) {
    URL.revokeObjectURL(img.dataset.previewUrl);
  });
  preview.innerHTML = '';

  Array.from(input.files || []).slice(0, 12).forEach(function (file, idx) {
    if (!file.type.startsWith('image/')) return;
    const url = URL.createObjectURL(file);
    const div = document.createElement('div');
    div.className = 'relative aspect-square rounded-xl overflow-hidden bg-cream group';
    const img = document.createElement('img');
    img.src = url;
    img.dataset.previewUrl = url;
    img.className = 'w-full h-full object-cover';
    div.appendChild(img);

    // 删除按钮（hover 显示）
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-ink/60 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity';
    btn.innerHTML = '<svg viewBox="0 0 24 24" class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>';
    btn.setAttribute('aria-label', '移除照片');
    btn.addEventListener('click', function(ev) {
      ev.preventDefault();
      ev.stopPropagation();
      removeFileFromInput(input, idx);
      div.remove();
    });
    div.appendChild(btn);

    preview.appendChild(div);
  });
});

// 从文件输入中移除指定索引的文件（使用 DataTransfer 重建 FileList）
function removeFileFromInput(input, removeIndex) {
  var dt = new DataTransfer();
  Array.from(input.files).forEach(function(file, i) {
    if (i !== removeIndex) dt.items.add(file);
  });
  input.files = dt.files;
}

// 滚动视差：时间轴卡片进入视口时渐入
(function () {
  function init() {
    const items = document.querySelectorAll('.timeline-item');
    if (!items.length) return;
    if (!('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('is-visible');
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

// 中轴线小太阳：吸附到「当前滚到视口中间最近的节点」，节点间平滑滑动
(function () {
  var sun = document.getElementById('timeline-sun');
  if (!sun) return;

  var prefersReduced = false;
  try {
    prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch (e) { /* ignore */ }

  var ticking = false;

  function nearestDot() {
    var wrapper = sun.closest('.timeline-line');
    if (!wrapper) return null;
    var viewportCenter = window.innerHeight / 2;
    var dots = wrapper.querySelectorAll('.timeline-dot');
    var best = null;
    var bestDist = Infinity;
    dots.forEach(function (dot) {
      var rect = dot.getBoundingClientRect();
      var dist = Math.abs(rect.top + rect.height / 2 - viewportCenter);
      if (dist < bestDist) {
        bestDist = dist;
        best = dot;
      }
    });
    return best;
  }

  function placeOn(dot) {
    if (!dot) return;
    // transform: translate3d 让动画在 GPU 合成层完成，避免滚动触发布局重算
    var dotRect = dot.getBoundingClientRect();
    var sunSize = sun.offsetHeight;
    var x = dotRect.left + (dotRect.width - sunSize) / 2;
    var y = dotRect.top + (dotRect.height - sunSize) / 2;
    sun.style.transform = 'translate3d(' + x + 'px, ' + y + 'px, 0)';
  }

  function update() {
    ticking = false;
    if (prefersReduced) {
      placeOn(nearestDot());
      return;
    }
    var dot = nearestDot();
    if (dot) {
      // 平滑过渡：直接设置 transform，CSS transition 负责滑动动画
      placeOn(dot);
    }
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  // 图片懒加载 / 字体加载 / 窗口变化都会改变布局，需重算以免圆点偏移
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  window.addEventListener('load', onScroll);
  if (document.readyState !== 'loading') onScroll();
  else document.addEventListener('DOMContentLoaded', onScroll);

  // 布局收敛：页面加载后布局可能仍漂移（图片/字体），
  // 用 rAF 循环直到最近节点位置连续稳定才停止。
  var lastPos = null;
  var stableFrames = 0;

  function stabilize() {
    var dot = nearestDot();
    if (!dot) {
      requestAnimationFrame(stabilize);
      return;
    }
    var rect = dot.getBoundingClientRect();
    var pos = Math.round(rect.top * 10);
    if (pos === lastPos) {
      stableFrames += 1;
    } else {
      lastPos = pos;
      stableFrames = 0;
    }
    update();
    if (stableFrames < 6) {
      requestAnimationFrame(stabilize);
    }
  }
  requestAnimationFrame(stabilize);
})();

// 上传照片（带进度条）
async function handleUpload(e) {
  e.preventDefault();  // 阻止原生表单提交，避免 XHR + 原生双重提交
  const form = e.target;
  const files = document.getElementById('upload-photos').files;
  if (!files.length) {
    alert('请先选择照片');
    return false;
  }

  const btn = document.getElementById('upload-btn');
  const progressWrap = document.getElementById('upload-progress');
  const bar = document.getElementById('progress-bar');
  const text = document.getElementById('progress-text');

  btn.disabled = true;
  btn.textContent = '上传中…';
  progressWrap.classList.remove('hidden');
  bar.style.width = '5%';
  text.textContent = '准备中…';

  const fd = new FormData(form);
  const xhr = new XMLHttpRequest();
  xhr.open('POST', form.action);

  xhr.upload.onprogress = function (ev) {
    if (ev.lengthComputable) {
      const pct = Math.round((ev.loaded / ev.total) * 100);
      bar.style.width = pct + '%';
      text.textContent = pct + '%';
    }
  };

  xhr.onload = function () {
    if (xhr.status >= 200 && xhr.status < 300) {
      location.reload();
    } else {
      bar.style.width = '100%';
      text.textContent = '上传失败';
      btn.disabled = false;
      btn.textContent = '重试';
    }
  };

  xhr.onerror = function () {
    bar.style.width = '100%';
    text.textContent = '网络错误';
    btn.disabled = false;
    btn.textContent = '重试';
  };

  xhr.send(fd);
  return false;
}
