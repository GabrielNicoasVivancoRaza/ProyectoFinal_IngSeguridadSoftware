/* Lógica de inicio de sesión y registro. */

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginMsg = document.getElementById("login-msg");
const regMsg = document.getElementById("reg-msg");

// Si ya hay sesión activa, ir directo al panel.
if (Auth.token) window.location.href = "dashboard.html";

document.getElementById("show-register").addEventListener("click", () => {
  loginForm.hidden = true;
  registerForm.hidden = false;
});

document.getElementById("show-login").addEventListener("click", () => {
  registerForm.hidden = true;
  loginForm.hidden = false;
});

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;

  // OAuth2 password flow: el login espera datos de formulario, no JSON.
  const form = new FormData();
  form.append("username", username);
  form.append("password", password);

  try {
    const data = await apiJson("/auth/login", { method: "POST", form });
    Auth.save(data.access_token, username);
    window.location.href = "dashboard.html";
  } catch (err) {
    showMsg(loginMsg, err.message, false);
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    username: document.getElementById("reg-username").value,
    email: document.getElementById("reg-email").value,
    password: document.getElementById("reg-password").value,
  };

  try {
    await apiJson("/auth/register", { method: "POST", body });
    showMsg(regMsg, "Cuenta creada. Ya puedes iniciar sesión.", true);
    setTimeout(() => document.getElementById("show-login").click(), 1200);
  } catch (err) {
    showMsg(regMsg, err.message, false);
  }
});
