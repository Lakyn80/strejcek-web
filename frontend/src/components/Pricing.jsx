import React from "react";
export default function Pricing() {
  return (
    <section id="cenik" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Orientační ceník - prodej</h2>
      <div className="overflow-x-auto">
        <table className="w-full border bg-white rounded-lg overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="text-left p-3 border">Komodita</th>
              <th className="text-left p-3 border">Cena orientačně</th>
              <th className="text-left p-3 border">Poznámka</th>
            </tr>
          </thead>
          <tbody>
            <tr><td className="p-3 border">Palety</td><td className="p-3 border">od 80 Kč / ks</td><td className="p-3 border">Cena dle stavu a množství</td></tr>
            <tr><td className="p-3 border">Big-bagy</td><td className="p-3 border">od 70 Kč / ks</td><td className="p-3 border">Dle objemu a stavu</td></tr>
            <tr><td className="p-3 border">Krabice</td><td className="p-3 border">od 3 Kč / ks</td><td className="p-3 border">Dle velikosti a množství</td></tr>
          </tbody>
        </table>
      </div>
      <p className="text-gray-600 text-sm mt-4">
        Ceny jsou orientační a upřesníme je dle objemu a vzdálenosti dopravy.
        Při větším odběru dovoz zajistíme. Menším odběratelům zasíláme poštou – poštovné hradí klient.
      </p>
    </section>
  );
}
