// frontend/src/lib/api.js
import axios from "axios";

// Pokud VITE_API_BASE_URL není zadáno, použij relativní cestu (produkce přes NGINX).
// V devu to prožene Vite proxy (viz vite.config.js) na http://127.0.0.1:5000
const API_BASE =
  (import.meta.env && import.meta.env.VITE_API_BASE_URL) ? import.meta.env.VITE_API_BASE_URL : "";

// POST /api/poptavka – odeslání formuláře
export async function postContact(payload) {
  try {
    const res = await axios.post(`${API_BASE}/api/poptavka`, payload, {
      headers: { "Content-Type": "application/json" },
      timeout: 15000,
    });
    return res.data; // očekává { ok: true, message: "..." }
  } catch (err) {
    // sjednocené chybové hlášení
    const status = err?.response?.status;
    const detail =
      err?.response?.data?.error ||
      err?.message ||
      "Neznámá chyba při odesílání.";
    throw new Error(`Chyba ${status ?? ""} ${detail}`.trim());
  }
}
