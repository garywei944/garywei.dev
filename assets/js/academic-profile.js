(() => {
  const section = document.querySelector('.academic-profile-identity-section');
  if (!section) return;

  const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reducedMotion) {
    section.querySelectorAll('.gsap-reveal').forEach((element) => {
      element.classList.remove('gsap-reveal');
    });
  }

  const reveal = section.querySelector('.academic-identity-reveal');
  const cover = section.querySelector('.academic-identity-cover');
  const frame = section.querySelector('.academic-identity-frame');
  const range = section.querySelector('.academic-identity-range');
  const mobileButtons = [...section.querySelectorAll('[data-view]')];

  const updateDivider = () => {
    const personal = Number(range.value);
    const academic = 100 - personal;
    frame.style.setProperty('--identity-split', `${personal}%`);
    range.setAttribute('aria-valuetext', `Personal view ${personal} percent, academic view ${academic} percent`);
  };

  const setMobileView = (view) => {
    frame.dataset.mobileView = view;
    mobileButtons.forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.view === view));
    });
  };

  const initializeReveal = () => {
    if (reducedMotion || !reveal || !cover || !('IntersectionObserver' in window)) return;

    let fallback;
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      window.clearTimeout(fallback);
      reveal.classList.remove('is-reveal-ready', 'is-revealing');
    };

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries.some((entry) => entry.isIntersecting)) return;
        observer.disconnect();
        reveal.classList.add('is-revealing');
        cover.addEventListener('animationend', finish, { once: true });
        fallback = window.setTimeout(finish, 2600);
      },
      { threshold: 0.12 }
    );

    reveal.classList.add('is-reveal-ready');
    observer.observe(reveal);
  };

  range.addEventListener('input', updateDivider);
  mobileButtons.forEach((button) => {
    button.addEventListener('click', () => setMobileView(button.dataset.view));
  });

  updateDivider();
  setMobileView(frame.dataset.mobileView);
  initializeReveal();
})();
