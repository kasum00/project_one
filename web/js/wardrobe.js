(function () {
  const input = document.getElementById("uploadMoreInput");
  const btn = document.getElementById("uploadMoreBtn");

  if (!input || !btn) return;

  btn.onclick = () => input.click();

  input.addEventListener("change", async () => {
    const files = Array.from(input.files || []);
    if (!files.length) return;

    const fd = new FormData();
    files.forEach((f) => fd.append("image", f));

    try {
      await apiFetch("/wardrobe/upload", {
        method: "POST",
        body: fd,
      });
      alert("Uploaded");
      location.reload();
    } catch (e) {
      alert(e.message);
    }
  });
})();
