(() => {
  const section = document.querySelector('.academic-profile-identity-section');
  if (!section) return;

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

  range.addEventListener('input', updateDivider);
  mobileButtons.forEach((button) => {
    button.addEventListener('click', () => setMobileView(button.dataset.view));
  });

  updateDivider();
  setMobileView(frame.dataset.mobileView);
})();
