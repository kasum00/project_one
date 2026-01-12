const form = document.querySelector(".forgot-form");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = form.email.value.trim();

  try {
    await apiFetch("/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    alert("Check your email");
  } catch (e) {
    alert(e.message);
  }
});
