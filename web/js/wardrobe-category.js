(async function () {
  const params = new URLSearchParams(window.location.search);
  const category = params.get("type");

  const grid = document.querySelector(".image-grid");
  if (!grid) return;

  try {
    const items = await apiFetch(
      `/wardrobe?category=${category}`
    );

    grid.innerHTML = "";

    if (!items.length) {
      grid.innerHTML = "<p>No items</p>";
      return;
    }

    items.forEach(item => {
      const img = document.createElement("img");


      img.src = `http://localhost:3000/${item.image_path}`;
      img.alt = item.ai_label || "wardrobe item";



      const wrapper = document.createElement("div");
      wrapper.className = "image-item";
      wrapper.appendChild(img);

      grid.appendChild(wrapper);
    });

  } catch (err) {
    console.error("LOAD WARDROBE ERROR:", err);
    grid.innerHTML = "<p>Error loading wardrobe</p>";
  }
})();
