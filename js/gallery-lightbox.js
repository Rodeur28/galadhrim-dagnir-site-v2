(function () {
  const root = document.getElementById('gd-lightbox');
  if (!root) return;

  const backdrop = root.querySelector('.gd-lightbox-backdrop');
  const imgEl = root.querySelector('.gd-lightbox-inner img');
  const captionEl = root.querySelector('.gd-lightbox-inner figcaption');
  const btnClose = root.querySelector('.gd-lightbox-close');
  const btnPrev = root.querySelector('.gd-lightbox-prev');
  const btnNext = root.querySelector('.gd-lightbox-next');

  const items = Array.from(document.querySelectorAll('.gallery > a[href]'));
  let index = 0;

  function captionFromLink(a) {
    const thumb = a.querySelector('img');
    return thumb && thumb.alt ? thumb.alt : '';
  }

  function show(i) {
    if (i < 0 || i >= items.length) return;
    index = i;
    const a = items[index];
    imgEl.src = a.getAttribute('href');
    imgEl.alt = captionFromLink(a);
    captionEl.textContent = captionFromLink(a);
    root.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    btnClose.focus();
  }

  function close() {
    root.classList.remove('is-open');
    document.body.style.overflow = '';
    imgEl.removeAttribute('src');
    imgEl.alt = '';
    captionEl.textContent = '';
  }

  items.forEach((a, i) => {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      show(i);
    });
  });

  backdrop.addEventListener('click', close);
  btnClose.addEventListener('click', close);

  btnPrev.addEventListener('click', function () {
    show((index - 1 + items.length) % items.length);
  });

  btnNext.addEventListener('click', function () {
    show((index + 1) % items.length);
  });

  document.addEventListener('keydown', function (e) {
    if (!root.classList.contains('is-open')) return;
    if (e.key === 'Escape') {
      close();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      show((index - 1 + items.length) % items.length);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      show((index + 1) % items.length);
    }
  });
})();
