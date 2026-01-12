const form = document.getElementById("loginForm");
const errBox = document.getElementById("login-error");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errBox.textContent = "";

  const email = form.email.value.trim();
  const password = form.password.value;

  try {
    const res = await apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    localStorage.setItem("token", res.token);
    window.location.href = "dashboard.html";
  } catch (err) {
    errBox.textContent = err.message;
  }
});
