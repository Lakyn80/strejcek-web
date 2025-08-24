import React from "react";
export default function WhatsAppButton() {
  const phone = import.meta.env.VITE_WHATSAPP_PHONE || "";
  const baseMsg = import.meta.env.VITE_WHATSAPP_MSG || "Dobrý den, mám zájem...";
  const msg = encodeURIComponent(baseMsg);
  if (!phone) return null;
  const href = `https://wa.me/${phone.replace(/\D/g, "")}?text=${msg}&utm_source=web&utm_medium=fab&utm_campaign=whatsapp`;
  return (
    <a href={href} target="_blank" aria-label="Chat na WhatsAppu" className="fixed bottom-5 right-5 rounded-full bg-green-500 hover:bg-green-600 shadow-lg p-4 text-white font-semibold">
      WA
    </a>
  );
}
