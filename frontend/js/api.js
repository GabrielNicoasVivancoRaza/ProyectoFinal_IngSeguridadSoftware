/* Cliente de la API: maneja la URL base y el token JWT. */

const API_BASE = "http://localhost:8000";
const TOKEN_KEY = "token";
const USER_KEY = "username";

const Auth = {
  get token() {
    return localStorage.getItem(TOKEN_KEY);
  },
  get username() {
    return localStorage.getItem(USER_KEY);
  },
  save(token, username) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, username);
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
  requireLogin() {
    if (!this.token) window.location.href = "index.html";
  },
};

/* Encabezado Authorization con el JWT. */
function authHeaders() {
  return Auth.token ? { Authorization: `Bearer ${Auth.token}` } : {};
}

/* Lanza un error legible a partir de la respuesta de la API. */
async function throwApiError(res) {
  let detail = `Error ${res.status}`;
  try {
    const body = await res.json();
    if (body.detail) {
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    }
  } catch {
    /* respuesta sin JSON */
  }
  if (res.status === 401) {
    Auth.clear();
    window.location.href = "index.html";
  }
  throw new Error(detail);
}

/* Peticiones que devuelven JSON. */
async function apiJson(path, { method = "GET", body, form } = {}) {
  const options = { method, headers: { ...authHeaders() } };

  if (form) {
    options.body = form; // FormData: el navegador pone el Content-Type
  } else if (body) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) await throwApiError(res);
  return res.status === 204 ? null : res.json();
}

/* Peticiones que devuelven un archivo binario (cifrado/descifrado). */
async function apiBlob(path, form) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: form,
  });
  if (!res.ok) await throwApiError(res);
  return res.blob();
}

/* Dispara la descarga de un blob en el navegador. */
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/* Muestra un mensaje de estado (ok / error). */
function showMsg(el, text, ok = true) {
  el.textContent = text;
  el.className = `msg ${ok ? "ok" : "err"}`;
}
