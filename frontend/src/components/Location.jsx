import React from "react";

export default function Location() {
  const address = "Polešovice 483, 687 37";
  const encoded = encodeURIComponent(address);
  const mapSrc = `https://www.google.com/maps?q=${encoded}&output=embed`;
  const directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encoded}`;

  return (
    <section id="lokalita" className="py-12">
      <h2 className="text-2xl font-bold mb-4">Lokalita / Vyzvednutí</h2>

      <p className="text-gray-700 mb-4">
        Sídlo: <span className="font-semibold">{address}</span>. 
        Můžete si přijet osobně, nebo po dohodě zajistíme dopravu – při větším odběru rozvážíme po celé ČR i Slovensku.
      </p>

      <div className="aspect-video w-full rounded-lg overflow-hidden bg-white border border-gray-200 shadow-md">
        <iframe
          title="Mapa – Polešovice 483, 687 37"
          src={mapSrc}
          className="w-full h-full"
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
        />
      </div>

      <div className="mt-4">
        <a
          href={directionsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-gray-900 text-white px-5 py-3 rounded shadow hover:bg-gray-800"
        >
          Trasa v Mapách
        </a>
      </div>
    </section>
  );
}
