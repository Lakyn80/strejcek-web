import React from "react";

export default function Hero() {
  const phone = import.meta.env.VITE_WHATSAPP_PHONE || "";
  const baseMsg = import.meta.env.VITE_WHATSAPP_MSG || "Dobrý den, mám zájem...";
  const msg = encodeURIComponent(baseMsg);
  const wa = phone
    ? `https://wa.me/${phone.replace(/\D/g, "")}?text=${msg}&utm_source=web&utm_medium=cta&utm_campaign=whatsapp`
    : "#";

  return (
    <header className="relative overflow-hidden bg-gray-900 text-white">
      {/* jemné gradientní “glow” pozadí */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-30"
        style={{
          background:
            "radial-gradient(60rem 30rem at 8% -10%, rgba(34,197,94,.45), transparent 40%), radial-gradient(52rem 30rem at 110% 30%, rgba(59,130,246,.35), transparent 38%)",
        }}
      />
      {/* decentní mřížka */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(255,255,255,0.2) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.2) 1px, transparent 1px)",
          backgroundSize: "36px 36px",
        }}
      />

      <div className="relative max-w-6xl mx-auto px-4 py-16 flex flex-col md:flex-row items-start md:items-center gap-8">
        <div className="flex-1">
          {/* NADPIS — zachován tvůj text, jen přidán gradient a typografie */}
          <h1 className="text-3xl md:text-5xl font-extrabold leading-tight tracking-tight">
            <span className="bg-gradient-to-r from-emerald-400 via-lime-300 to-sky-400 bg-clip-text text-transparent drop-shadow-sm">
              Palety • Big-Bagy • Krabice
            </span>
            <span className="block text-white/90 mt-1 md:mt-2">
              Prodej &amp; Výkup
            </span>
          </h1>

          <p className="mt-4 text-base md:text-lg text-gray-300 max-w-2xl">
            Výkup a prodej opotřebených palet, big-bagů a krabic v okolí Polešovic u Uherského Hradiště.
            Přijeďte si osobně, nebo po dohodě zajistíme dopravu – při větším odběru rozvážíme po celé ČR i Slovensku.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="#kontakt"
              className="group relative inline-flex items-center gap-2 rounded-md bg-white px-5 py-3 font-semibold text-gray-900 transition hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-white/40"
            >
              <span>Poptat</span>
              <span className="inline-block transition-transform group-hover:translate-x-0.5">→</span>
            </a>
            <a
              href={wa}
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-2 rounded-md bg-emerald-500 px-5 py-3 font-semibold text-white shadow-lg shadow-emerald-500/20 transition hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              <span className="inline-block h-2 w-2 rounded-full bg-white animate-pulse" />
              <span>Napsat na WhatsApp</span>
            </a>
          </div>
        </div>

        {/* obrázková mozaika — stejné cesty, jen hezčí rámeček/hover */}
        <div className="flex-1 grid grid-cols-3 gap-2 opacity-95">
          {[
            { src: "/images/bag_2.jpg", alt: "Big-bag" },
            { src: "/images/palety_drev_1.jpg", alt: "Palety" },
            { src: "/images/krab_3.jpg", alt: "Krabice" },
            { src: "/images/hranol_drev_1.jpg", alt: "Dřevěný hranol" },
            { src: "/images/palety_5.jpg", alt: "Palety" },
            { src: "/images/palety_6.jpg", alt: "Palety" },
          ].map((img, i) => (
            <div
              key={i}
              className="relative overflow-hidden rounded-xl border border-white/10 bg-white/5"
            >
              <img
                src={img.src}
                alt={img.alt}
                loading="eager"
                className="h-28 w-full object-cover transition duration-300 hover:scale-[1.03]"
              />
              {/* jemný lesk při hoveru */}
              <div
                className="pointer-events-none absolute inset-0 opacity-0 transition-opacity hover:opacity-100"
                style={{
                  background:
                    "linear-gradient(120deg, transparent 20%, rgba(255,255,255,.08) 40%, transparent 60%)",
                }}
              />
            </div>
          ))}
        </div>
      </div>
    </header>
  );
}
