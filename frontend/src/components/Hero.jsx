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
          {/* NADPIS */}
          <h1 className="text-3xl md:text-5xl font-extrabold leading-tight tracking-tight">
            <span className="bg-gradient-to-r from-emerald-400 via-lime-300 to-sky-400 bg-clip-text text-transparent drop-shadow-sm">
              Palety • Big-Bagy • Krabice
            </span>
            <span className="block text-white/90 mt-1 md:mt-2">
              Prodej &amp; Výkup
            </span>
          </h1>

          {/* DŮRAZ NA PVM — moderní, bez teček */}
          <p className="mt-3 inline-flex items-center gap-3 text-sm md:text-base font-semibold text-emerald-300 bg-white/5 px-4 py-2 rounded-lg shadow-sm tracking-wide">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-extrabold text-lg">P&nbsp;V&nbsp;M</span>
            <span className="text-gray-200">= Pomocný výrobní materiál</span>
          </p>

          {/* ÚVODNÍ TEXT */}
          <p className="mt-4 text-base md:text-lg text-gray-300 max-w-2xl">
            Výkupujeme a prodáváme použité palety, big-bagy a krabice. Sídlíme v{" "}
            <strong>Polešovicích u Uherského Hradiště</strong>. Přijeďte si
            osobně, nebo po dohodě zajistíme dopravu –{" "}
            <strong>při větším odběru rozvážíme po celé ČR i Slovensku.</strong>
          </p>

          {/* Odkazy místo navbaru – jen smooth scroll na sekce */}
          <nav className="mt-6 flex flex-wrap gap-2">
            <a href="#produkty" className="px-4 py-2 rounded bg-white/10 text-white hover:bg-white/20 transition">
              Nabídka
            </a>
            <a href="#cenik" className="px-4 py-2 rounded bg-white/10 text-white hover:bg-white/20 transition">
              Ceník
            </a>
            <a href="#galerie" className="px-4 py-2 rounded bg-white/10 text-white hover:bg-white/20 transition">
              Galerie
            </a>
            <a href="#likvidace" className="px-4 py-2 rounded bg-white/10 text-white hover:bg-white/20 transition">
              Likvidace
            </a>
            <a href="#kontakt" className="px-4 py-2 rounded bg-white/10 text-white hover:bg-white/20 transition">
              Kontakt
            </a>
          </nav>


          {/* volitelně můžeš nechat i WhatsApp CTA — nechávám zapojené proměnné, ale nevkládám tlačítko, jak sis přál */}
          {/* <a href={wa} target="_blank" rel="noopener noreferrer" className="mt-3 inline-block underline">
            WhatsApp
          </a> */}
        </div>

        {/* Obrázková mřížka vpravo – nechávám beze změny logiky (jen si drž své src podle toho, co máš v /public/images) */}
        <div className="flex-1 grid grid-cols-3 gap-2 opacity-95">
          {[
            { src: "/images/bagy_2.webp", alt: "Big-bag" },
            { src: "/images/palety_drev_1.webp", alt: "Palety" },
            { src: "/images/krab_3.webp", alt: "Krabice" },
            { src: "/images/hranol_drev_1.webp", alt: "Dřevěný hranol" },
            { src: "/images/palety_5.webp", alt: "Palety" },
            { src: "/images/palety_6.webp", alt: "Palety" },
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
