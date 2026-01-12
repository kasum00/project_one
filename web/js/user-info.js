(function () {
  apiFetch("/users/me")
    .then((u) => {
      const nameEl = document.getElementById("username");
      const emailEl = document.getElementById("email");

      if (nameEl) nameEl.textContent = u.username || "User";
      if (emailEl) emailEl.textContent = u.email || "";
    })
    .catch(() => {
      localStorage.removeItem("token");
      window.location.href = "login.html";
    });
})();
