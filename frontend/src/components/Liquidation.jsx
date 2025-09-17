import React from "react";
import { CheckCircle } from "lucide-react";

export default function Liquidation() {
  return (
    <section
      id="likvidace"
      className="py-20 bg-gradient-to-b from-white to-gray-50"
    >
      <div className="max-w-5xl mx-auto px-6 text-center">
        <h2 className="text-4xl md:text-5xl font-extrabold mb-6 text-gray-900">
          🏭 Likvidace zásob &amp; materiálu
        </h2>

        {/* Upravený text dle zadání */}
        <p className="text-lg md:text-xl text-gray-700 mb-6 leading-relaxed max-w-3xl mx-auto">
          Pomůžeme vám <strong>rychle a výhodně</strong> s{" "}
          <strong>odkupem materiálu</strong>, který zůstává po výrobě, nebo při
          likvidaci firmy. Vykupujeme{" "}
          <strong>nejenom palety, big-bagy, krabice, dřevo</strong> i{" "}
          <strong>další</strong> – prostě cokoliv, co má hodnotu,{" "}
          <strong>vykoupíme za férovou cenu</strong> a <strong>odvezeme</strong>.
        </p>

        <div className="grid md:grid-cols-2 gap-6 mb-12 max-w-3xl mx-auto">
          {[
            "Odkoupíme téměř jakýkoliv materiál",
            "Rychlé vyklizení skladů a areálů",
            "Okamžitá platba a férové podmínky",
            "Snížení nákladů na likvidaci",
          ].map((text, i) => (
            <div
              key={i}
              className="flex items-center justify-center bg-white shadow rounded-xl p-4"
            >
              <CheckCircle className="text-green-600 mr-3" size={22} />
              <span className="text-gray-800 font-medium">{text}</span>
            </div>
          ))}
        </div>

        <p className="text-lg md:text-xl font-semibold text-gray-800 mb-10">
          ➡️ Pošlete nám seznam nebo fotografie zásob – ozveme se obratem.
        </p>

        <a
          href="#kontakt"
          onClick={(e) => {
            e.preventDefault();
            // nastav hash na #likvidace (ContactForm to pozná)
            window.location.hash = "likvidace";
            // a posuň stránku na formulář
            document.getElementById("kontakt")?.scrollIntoView({ behavior: "smooth" });
          }}
          className="inline-block bg-gradient-to-r from-gray-900 to-gray-700 text-white px-10 py-4 rounded-xl shadow-lg hover:scale-105 transform transition"
        >
          Odeslat poptávku na likvidaci
        </a>
      </div>
    </section>
  );
}
