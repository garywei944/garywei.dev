$(function () {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const $form = $(form);
  const $warning = $('#form-message-warning');
  const $success = $('#form-message-success');
  const submit = form.querySelector('[type="submit"]');

  async function handleSubmit(event) {
    event.preventDefault();
    const data = new FormData(event.target);

    submit.disabled = true;
    $warning.hide();
    $success.hide();

    try {
      const response = await fetch(event.target.action, {
        method: form.method,
        body: data,
        headers: {
          Accept: 'application/json',
        },
      });

      if (!response.ok) throw new Error(`Form submission failed with status ${response.status}`);

      setTimeout(function () {
        $form.fadeOut();
      }, 1000);
      setTimeout(function () {
        $success.fadeIn();
      }, 1400);
    } catch (error) {
      $warning.text('Something went wrong. Please try again.').fadeIn();
      submit.disabled = false;
    }
  }

  form.addEventListener('submit', handleSubmit);
});
