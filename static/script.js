document.addEventListener("DOMContentLoaded", () => {
  const encodeForm = document.querySelector("form[action='/encode']");

  if (encodeForm) {
    encodeForm.addEventListener("submit", (e) => {
      const image = encodeForm.querySelector("input[name='image']").files[0];
      const message = encodeForm
        .querySelector("textarea[name='message']")
        .value.trim();

      if (!image) {
        alert("Please upload an image.");
        e.preventDefault();
        return;
      }

      if (!image.name.toLowerCase().endsWith(".png")) {
        alert("Use PNG images only. JPG may corrupt hidden data.");
        e.preventDefault();
        return;
      }

      if (message.length === 0) {
        alert("Message cannot be empty.");
        e.preventDefault();
        return;
      }

      encodeForm.querySelector("button").innerText = "Encoding...";
    });
  }
});
