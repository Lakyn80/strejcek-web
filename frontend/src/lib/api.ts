// Pokud VITE_API_BASE_URL není zadáno, použij relativní cestu (produkce přes NGINX).
// V devu to prožene Vite proxy (viz vite.config.ts) na http://127.0.0.1:5000
const API_BASE =
  import.meta.env.VITE_API_BASE_URL ?? "";

export interface ContactPayload {
  name: string;
  email: string;
  itemType: string;
  message: string;
  phone?: string;
  quantity?: string;
  location?: string;
  delivery?: boolean;
  pickup?: boolean;
  captchaToken?: string;
}

// POST /api/poptavka – odeslání formuláře
export async function postContact(payload: ContactPayload): Promise<{ ok: boolean; message?: string }> {
  const res = await fetch(`${API_BASE}/api/poptavka`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(15000),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data?.error ?? `HTTP ${res.status}`;
    throw new Error(detail);
  }

  return data;
}
