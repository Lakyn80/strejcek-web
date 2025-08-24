import React from "react";
export default function Location() {
  return (
    <section id="lokalita" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Lokalita / Vyzvednutí</h2>
      <p className="text-gray-700 mb-4">
        Sídlo: Polešovice u Uherského Hradiště. Můžete si přijet, nebo po dohodě přivezeme u většího odběru.
      </p>
      <div className="aspect-video w-full rounded-lg overflow-hidden border bg-white">
        <iframe
          title="mapa"
          src="https://www.google.com/maps?q=Pole%C5%A1ovice&output=embed"
          className="w-full h-full"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        ></iframe>
      </div>
    </section>
  );
}
