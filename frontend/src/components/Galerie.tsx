import { useState } from "react";
import { X, ChevronLeft, ChevronRight } from "lucide-react";

const photos = [
  // Palety
  { src: "/images/pvm-deal_webp_gallrey_imgs/palety_1.webp", alt: "Europalety" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/palety_2.webp", alt: "Palety skladem" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/palety_3.webp", alt: "Dřevěné palety" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/palety_4.webp", alt: "Palety výkup" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/palety_5.webp", alt: "Palety venkovní sklad" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/palety_6.webp", alt: "Palety připravené k odvozu" },
  // Big-bagy
  { src: "/images/pvm-deal_webp_gallrey_imgs/bagy_1.webp", alt: "Big-bagy skladem" },
  { src: "/images/bagy_2.webp", alt: "Big-bagy – výkup" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/bagy_3.webp", alt: "Big-bagy balené" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/bagy_4.webp", alt: "Big-bagy různé rozměry" },
  // Krabice
  { src: "/images/pvm-deal_webp_gallrey_imgs/krab_1.webp", alt: "Kartonové krabice" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/krab_2.webp", alt: "Krabice skladem" },
  { src: "/images/krab_3.webp", alt: "Krabice různé rozměry" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/krab_4.webp", alt: "Krabice výkup" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/krab_5.webp", alt: "Krabice balené" },
  // Dřevo & ostatní
  { src: "/images/hranol_drev_1.webp", alt: "Dřevěné hranoly" },
  { src: "/images/palety_drev_1.webp", alt: "Dřevěné palety – detail" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/hranol_drev_1.webp", alt: "Hranoly ze skladu" },
  // Fotky z terénu
  { src: "/images/pvm-deal_webp_gallrey_imgs/IMG-20250830-WA0001.webp", alt: "Sklad PVM Deal" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/IMG-20250830-WA0002.webp", alt: "Sklad PVM Deal" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/IMG-20250830-WA0003.webp", alt: "Sklad PVM Deal" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/IMG-20250830-WA0004.webp", alt: "Sklad PVM Deal" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/IMG-20250903-WA0012.webp", alt: "Provoz PVM Deal" },
  { src: "/images/pvm-deal_webp_gallrey_imgs/IMG-20250903-WA0013.webp", alt: "Provoz PVM Deal" },
];

const Galerie = () => {
  const [lightbox, setLightbox] = useState<number | null>(null);

  const prev = () => setLightbox((i) => (i !== null ? (i - 1 + photos.length) % photos.length : 0));
  const next = () => setLightbox((i) => (i !== null ? (i + 1) % photos.length : 0));

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowLeft") prev();
    if (e.key === "ArrowRight") next();
    if (e.key === "Escape") setLightbox(null);
  };

  return (
    <section id="galerie" className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-14">
          <h2 className="font-display text-4xl sm:text-5xl text-foreground">
            Foto<span className="text-primary">galerie</span>
          </h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {photos.map((photo, i) => (
            <button
              key={i}
              onClick={() => setLightbox(i)}
              className="group relative rounded-lg overflow-hidden border border-border aspect-[4/3] focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <img
                src={photo.src}
                alt={photo.alt}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-background/0 group-hover:bg-background/40 transition-colors flex items-center justify-center">
                <span className="text-foreground opacity-0 group-hover:opacity-100 transition-opacity font-display text-lg">
                  Zobrazit
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Lightbox */}
      {lightbox !== null && (
        <div
          className="fixed inset-0 z-50 bg-background/95 flex items-center justify-center p-4"
          onClick={() => setLightbox(null)}
          onKeyDown={handleKeyDown}
          tabIndex={0}
        >
          <button
            className="absolute top-4 right-4 text-foreground hover:text-primary transition-colors z-10"
            onClick={() => setLightbox(null)}
            aria-label="Zavřít"
          >
            <X size={32} />
          </button>

          <button
            className="absolute left-4 top-1/2 -translate-y-1/2 text-foreground hover:text-primary transition-colors z-10 bg-background/50 rounded-full p-2"
            onClick={(e) => { e.stopPropagation(); prev(); }}
            aria-label="Předchozí"
          >
            <ChevronLeft size={28} />
          </button>

          <img
            src={photos[lightbox].src}
            alt={photos[lightbox].alt}
            className="max-w-full max-h-[85vh] rounded-lg object-contain"
            onClick={(e) => e.stopPropagation()}
          />

          <button
            className="absolute right-4 top-1/2 -translate-y-1/2 text-foreground hover:text-primary transition-colors z-10 bg-background/50 rounded-full p-2"
            onClick={(e) => { e.stopPropagation(); next(); }}
            aria-label="Další"
          >
            <ChevronRight size={28} />
          </button>

          <p className="absolute bottom-4 left-1/2 -translate-x-1/2 text-sm text-muted-foreground">
            {lightbox + 1} / {photos.length}
          </p>
        </div>
      )}
    </section>
  );
};

export default Galerie;
