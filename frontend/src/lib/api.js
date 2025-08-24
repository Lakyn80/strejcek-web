import axios from "axios";
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";
export async function postContact(payload) {
  const res = await axios.post(`${API_BASE}/api/contact`, payload, {
    headers: { "Content-Type": "application/json" }
  });
  return res.data;
}
