import React from "react";

const imgs = [
  "/images/palety_1.webp",
  "/images/palety_2.webp",
  "/images/palety_3.webp",
  "/images/palety_4.webp",
  "/images/palety_5.webp",
  "/images/palety_6.webp",
];

export default function Gallery() {
  return (
    <section id="galerie" className="py-12">
      <h2 className="text-2xl font-bold mb-6">Fotogalerie</h2>
      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
        {imgs.map((src, i) => (
          <img
            key={i}
            src={src}
            loading="lazy"
            alt={`galerie-${i}`}
            className="w-full h-48 object-cover rounded-lg border bg-white shadow-sm"
          />
        ))}
      </div>
    </section>
  );
}
