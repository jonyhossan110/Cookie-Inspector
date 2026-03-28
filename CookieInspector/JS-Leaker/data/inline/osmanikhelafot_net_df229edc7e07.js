
document.addEventListener("DOMContentLoaded", function() {
  const popup = document.getElementById("homepage-popup");
  const removeBtn = document.getElementById("popup-remove");

  // Show popup instantly on page load/redirect
  popup.style.display = "flex";

  // Auto hide after 5 seconds if user doesn’t close manually
  const autoClose = setTimeout(() => {
    popup.style.display = "none";
  }, 5000);

  // Manual close
  removeBtn.addEventListener("click", () => {
    popup.style.display = "none";
    clearTimeout(autoClose);
  });

  // Close when clicking outside popup
  popup.addEventListener("click", (e) => {
    if (e.target === popup) {
      popup.style.display = "none";
      clearTimeout(autoClose);
    }
  });
});
