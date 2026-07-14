/* Lógica del panel: documentos, cifrado, firma, certificados y auditoría. */

Auth.requireLogin();
document.getElementById("current-user").textContent = Auth.username || "";

document.getElementById("logout").addEventListener("click", () => {
  Auth.clear();
  window.location.href = "index.html";
});

/* --- Navegación por pestañas --- */
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll("section").forEach((s) => s.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(tab.dataset.tab).classList.add("active");
    if (tab.dataset.tab === "audit") loadAudit();
    if (tab.dataset.tab === "certificates") loadCertificates();
  });
});

const $ = (id) => document.getElementById(id);

/* ================= DOCUMENTOS ================= */

const uploadMsg = $("upload-msg");

$("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = $("doc-file").files[0];
  const form = new FormData();
  form.append("file", file);

  try {
    const doc = await apiJson("/documents", { method: "POST", form });
    showMsg(uploadMsg, `Subido. SHA-256: ${doc.sha256.slice(0, 24)}...`, true);
    $("upload-form").reset();
    loadDocuments();
  } catch (err) {
    showMsg(uploadMsg, err.message, false);
  }
});

async function loadDocuments() {
  const body = $("documents-body");
  try {
    const docs = await apiJson("/documents");
    body.innerHTML = "";
    docs.forEach((doc) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${doc.id}</td>
        <td>${doc.filename}</td>
        <td class="mono">${doc.sha256.slice(0, 32)}...</td>
        <td class="actions">
          <button class="secondary" data-verify="${doc.id}">Verificar</button>
          <button class="danger" data-delete="${doc.id}">Eliminar</button>
        </td>`;
      body.appendChild(tr);
    });
  } catch (err) {
    showMsg($("documents-msg"), err.message, false);
  }
}

/* Delegación de eventos para verificar/eliminar documentos. */
$("documents-body").addEventListener("click", async (e) => {
  const verifyId = e.target.dataset.verify;
  const deleteId = e.target.dataset.delete;
  const msg = $("documents-msg");

  try {
    if (verifyId) {
      const res = await apiJson(`/documents/${verifyId}/verify`);
      showMsg(msg, `Documento ${verifyId}: ${res.detail}`, res.valid);
    } else if (deleteId) {
      await apiJson(`/documents/${deleteId}`, { method: "DELETE" });
      showMsg(msg, `Documento ${deleteId} eliminado.`, true);
      loadDocuments();
    }
  } catch (err) {
    showMsg(msg, err.message, false);
  }
});

/* ================= CIFRADO AES ================= */

$("encrypt-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = $("enc-file").files[0];
  const form = new FormData();
  form.append("file", file);
  form.append("password", $("enc-password").value);

  try {
    const blob = await apiBlob("/crypto/encrypt", form);
    downloadBlob(blob, `${file.name}.enc`);
    showMsg($("encrypt-msg"), "Archivo cifrado y descargado.", true);
  } catch (err) {
    showMsg($("encrypt-msg"), err.message, false);
  }
});

$("decrypt-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = $("dec-file").files[0];
  const form = new FormData();
  form.append("file", file);
  form.append("password", $("dec-password").value);

  try {
    const blob = await apiBlob("/crypto/decrypt", form);
    downloadBlob(blob, file.name.replace(/\.enc$/, "") || "archivo");
    showMsg($("decrypt-msg"), "Archivo descifrado y descargado.", true);
  } catch (err) {
    showMsg($("decrypt-msg"), err.message, false);
  }
});

/* ================= FIRMA RSA ================= */

$("genkeys-btn").addEventListener("click", async () => {
  try {
    const keys = await apiJson("/crypto/keys/generate", { method: "POST" });
    $("priv-key").value = keys.private_key_pem;
    $("pub-key").value = keys.public_key_pem;
  } catch (err) {
    showMsg($("sign-msg"), err.message, false);
  }
});

$("sign-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData();
  form.append("file", $("sign-file").files[0]);
  form.append("private_key_pem", $("priv-key").value);

  try {
    const res = await apiJson("/crypto/sign", { method: "POST", form });
    $("signature-b64").value = res.signature_b64;
    showMsg($("sign-msg"), `Documento firmado (${res.algorithm}).`, true);
  } catch (err) {
    showMsg($("sign-msg"), err.message, false);
  }
});

$("verify-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData();
  form.append("file", $("verify-file").files[0]);
  form.append("public_key_pem", $("pub-key").value);
  form.append("signature_b64", $("signature-b64").value);

  try {
    const res = await apiJson("/crypto/verify", { method: "POST", form });
    showMsg($("verify-msg"), res.detail, res.valid);
  } catch (err) {
    showMsg($("verify-msg"), err.message, false);
  }
});

/* ================= CERTIFICADOS ================= */

$("issue-cert-btn").addEventListener("click", async () => {
  try {
    const cert = await apiJson("/certificates", { method: "POST" });
    $("cert-pem-label").hidden = false;
    $("cert-pem").hidden = false;
    $("cert-pem").value = cert.cert_pem;
    showMsg($("cert-msg"), `Certificado emitido. Serial: ${cert.serial}`, true);
    loadCertificates();
  } catch (err) {
    showMsg($("cert-msg"), err.message, false);
  }
});

async function loadCertificates() {
  const body = $("certificates-body");
  try {
    const certs = await apiJson("/certificates");
    body.innerHTML = "";
    certs.forEach((c) => {
      const estado = c.status === "valid" ? "ok" : "err";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${c.id}</td>
        <td class="mono">${c.serial.slice(0, 16)}...</td>
        <td><span class="badge ${estado}">${c.status}</span></td>
        <td>${new Date(c.expires_at).toLocaleDateString()}</td>
        <td class="actions">
          <button class="secondary" data-validate="${c.id}">Validar</button>
          <button class="danger" data-revoke="${c.id}">Revocar</button>
        </td>`;
      body.appendChild(tr);
    });
  } catch (err) {
    showMsg($("cert-msg"), err.message, false);
  }
}

$("certificates-body").addEventListener("click", async (e) => {
  const validateId = e.target.dataset.validate;
  const revokeId = e.target.dataset.revoke;
  const msg = $("cert-msg");

  try {
    if (validateId) {
      const res = await apiJson(`/certificates/${validateId}/validate`);
      showMsg(msg, `Certificado ${validateId}: ${res.detail}`, res.valid);
    } else if (revokeId) {
      await apiJson(`/certificates/${revokeId}/revoke`, { method: "POST" });
      showMsg(msg, `Certificado ${revokeId} revocado.`, true);
      loadCertificates();
    }
  } catch (err) {
    showMsg(msg, err.message, false);
  }
});

/* ================= AUDITORÍA ================= */

async function loadAudit() {
  const body = $("audit-body");
  try {
    const logs = await apiJson("/audit/logs");
    body.innerHTML = "";
    logs.forEach((log) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${new Date(log.created_at).toLocaleString()}</td>
        <td>${log.event_type}</td>
        <td>${log.detail ?? "-"}</td>
        <td class="mono">${log.ip ?? "-"}</td>`;
      body.appendChild(tr);
    });
  } catch {
    /* la sesión expirada ya redirige al login */
  }
}

$("refresh-audit").addEventListener("click", loadAudit);

/* Carga inicial */
loadDocuments();
