$(function () {
  let form = document.getElementById("contactForm");

  async function handleSubmit(event) {
    event.preventDefault();
    let data = new FormData(event.target);
    fetch(event.target.action, {
      method: form.method,
      body: data,
      headers: {
        Accept: "application/json",
      },
    })
      .then((response) => {
        $("#form-message-warning").hide();
        setTimeout(function () {
          $("#contactForm").fadeOut();
        }, 1000);
        setTimeout(function () {
          $("#form-message-success").fadeIn();
        }, 1400);
      })
      .catch((error) => {
        $("#form-message-warning").html("Something went wrong. Please try again.");
        $("#form-message-warning").fadeIn();
        $submit.css("display", "none");
      });
  }

  form.addEventListener("submit", handleSubmit);
});
