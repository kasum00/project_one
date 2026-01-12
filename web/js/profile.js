(function () {
  apiFetch("/users/me").then((u) => {
    document.getElementById("profile-name").textContent = u.username;
    document.getElementById("profile-email").textContent = u.email;
  });
})();
