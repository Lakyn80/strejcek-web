// src/components/Gallery.jsx
import React, { useState } from "react";
import GalleryModal from "./GalleryModal.jsx";
import { GALLERY_IMAGES, HOMEPAGE_LIMIT } from "../data/galleryImages";

// Bezpečný obrázek – když cesta neexistuje, tile se skryje
function SafeImg({ src, alt, className }) {
  const [ok, setOk] = useState(true);
  if (!ok) return null;
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className={className}
      onError={() => setOk(false)}
    />
  );
}

export default function Gallery() {
  const [open, setOpen] = useState(false);

  // vezmeme prvních pár fotek na homepage
  const preview = GALLERY_IMAGES.slice(0, HOMEPAGE_LIMIT);

  return (
    <section id="galerie" className="py-12">
      <div className="flex items-end justify-between mb-6">
        <h2 className="text-2xl font-bold">Fotogalerie</h2>
        <button
          onClick={() => setOpen(true)}
          className="text-sm px-4 py-2 rounded bg-gray-900 text-white hover:bg-gray-800"
        >
          Zobrazit celou galerii
        </button>
      </div>

      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
        {preview.map((src, i) => (
          <SafeImg
            key={src + i}
            src={src}
            alt={`galerie-${i}`}
            className="w-full h-48 object-cover rounded-lg border bg-white shadow-sm"
          />
        ))}
      </div>

      {/* Modal s celou galerií */}
      <GalleryModal
        open={open}
        onClose={() => setOpen(false)}
        images={GALLERY_IMAGES}
      />
    </section>
  );
}
