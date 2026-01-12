(function () {
  const uploadInput = document.getElementById("uploadInput");
  const goChatbotBtn = document.getElementById("goChatbotBtn");

  if (!uploadInput) return;

  uploadInput.addEventListener("change", async () => {
    const files = Array.from(uploadInput.files || []);

    if (!files.length) {
      showToast("Please select at least one image", "warning");
      return;
    }

    const fd = new FormData();
    files.forEach((f) => fd.append("image", f)); 

    try {
      showToast("Uploading wardrobe...", "warning");

      await apiFetch("/wardrobe/upload", {
        method: "POST",
        body: fd,
      });

      showToast("Upload successful 🎉", "success");
      uploadInput.value = "";
    } catch (e) {
      showToast(e.message || "Upload failed ❌", "error");
    }
  });
})();
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 10);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
