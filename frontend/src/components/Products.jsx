import React from "react";
const cards = [
  { title: "Palety", desc: "Europalety, jednorázové i atypické. Stav dle dohody." },
  { title: "Big-bagy", desc: "Různé objemy a stavy, vhodné pro sypké materiály." },
  { title: "Krabice", desc: "Kartony a krabice všech druhů a velikostí." }
];
export default function Products() {
  return (
    <section id="produkty" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Co prodáváme a vykupujeme</h2>
      <div className="grid md:grid-cols-3 gap-6">
        {cards.map(c => (
          <div key={c.title} className="border rounded-lg p-5 bg-white shadow-sm">
            <h3 className="text-xl font-semibold">{c.title}</h3>
            <p className="text-gray-600 mt-2">{c.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
