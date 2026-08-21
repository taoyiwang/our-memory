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

  Array.from(input.files || []).slice(0, 12).forEach(function (file) {
    if (!file.type.startsWith('image/')) return;
    const url = URL.createObjectURL(file);
    const div = document.createElement('div');
    div.className = 'relative aspect-square rounded-xl overflow-hidden bg-cream';
    const img = document.createElement('img');
    img.src = url;
    img.dataset.previewUrl = url;
    img.className = 'w-full h-full object-cover';
    div.appendChild(img);
    preview.appendChild(div);
  });
});

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

// 上传照片（带进度条）
async function handleUpload(e) {
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
