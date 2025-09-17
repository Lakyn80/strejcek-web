import React from "react";

const cards = [
  {
    title: "Palety",
    desc:
      "Ve velkém množství: dřevěné i plastové, typické (EURO) i atypické rozměry. Stav a cena dle dohody a objemu.",
  },
  {
    title: "Big-bagy",
    desc:
      "Celé portfolio rozměrů: od nejmenších za akční cenu od 50 Kč/ks až po největší vyráběné typy (u velkých mírně vyšší cena kvůli materiálu).",
  },
  {
    title: "Krabice",
    desc:
      "Ceny startují už od 1 Kč/ks. Rozumné 3-vln střední velikosti od 3 Kč/ks, 5-vln od 4,5 Kč/ks.",
  },
];

export default function Products() {
  return (
    <section id="produkty" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Co prodáváme a vykupujeme</h2>
      <div className="grid md:grid-cols-3 gap-6">
        {cards.map((c) => (
          <div key={c.title} className="border rounded-lg p-5 bg-white shadow-sm">
            <h3 className="text-xl font-semibold">{c.title}</h3>
            <p className="text-gray-600 mt-2">{c.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
