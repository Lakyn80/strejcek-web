import React from "react";

export default function Pricing() {
  return (
    <section id="cenik" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Orientační ceník – prodej</h2>
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
            <tr>
              <td className="p-3 border">Palety</td>
              <td className="p-3 border">dle dohody</td>
              <td className="p-3 border">
                Dřevěné i plastové, typické i atypické; cena podle stavu a objemu.
              </td>
            </tr>
            <tr>
              <td className="p-3 border">Big-bagy (nejmenší)</td>
              <td className="p-3 border"><strong>od 50 Kč / ks</strong></td>
              <td className="p-3 border">Akční cena u nejmenších rozměrů.</td>
            </tr>
            <tr>
              <td className="p-3 border">Big-bagy (největší)</td>
              <td className="p-3 border">+ mírný příplatek</td>
              <td className="p-3 border">
                U největších typů je vyšší spotřeba materiálu → mírně zvýšená cena.
              </td>
            </tr>
            <tr>
              <td className="p-3 border">Krabice – různé</td>
              <td className="p-3 border"><strong>od 1 Kč / ks</strong></td>
              <td className="p-3 border">Nejnižší startovní cena.</td>
            </tr>
            <tr>
              <td className="p-3 border">Krabice – 3-vln (střední)</td>
              <td className="p-3 border"><strong>od 3 Kč / ks</strong></td>
              <td className="p-3 border">Rozumný poměr cena/výkon.</td>
            </tr>
            <tr>
              <td className="p-3 border">Krabice – 5-vln</td>
              <td className="p-3 border"><strong>od 4,5 Kč / ks</strong></td>
              <td className="p-3 border">Vyšší pevnost, pro těžší zboží.</td>
            </tr>
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
