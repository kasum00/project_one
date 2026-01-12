const form = document.querySelector("form");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const name = document.getElementById("name").value.trim();

  try {
    await apiFetch("/users/setup-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });

    window.location.href = "dashboard.html";
  } catch (e) {
    alert(e.message);
  }
});
