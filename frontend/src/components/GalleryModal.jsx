// src/components/GalleryModal.jsx
import React, { useEffect, useState, useCallback } from "react";
import { MODAL_PAGE_SIZE } from "../data/galleryImages";

export default function GalleryModal({ open, onClose, images }) {
  const [page, setPage] = useState(1);
  const [lightboxIndex, setLightboxIndex] = useState(null);

  const totalShown = page * MODAL_PAGE_SIZE;
  const canLoadMore = totalShown < images.length;

  const closeLightbox = useCallback(() => setLightboxIndex(null), []);
  const showPrev = useCallback(
    () => setLightboxIndex((i) => (i === null ? null : (i - 1 + images.length) % images.length)),
    [images.length]
  );
  const showNext = useCallback(
    () => setLightboxIndex((i) => (i === null ? null : (i + 1) % images.length)),
    [images.length]
  );

  // ESC a šipky v lightboxu / zavření modalu
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") {
        if (lightboxIndex !== null) closeLightbox();
        else onClose?.();
      } else if (lightboxIndex !== null && (e.key === "ArrowRight" || e.key === "ArrowDown")) {
        showNext();
      } else if (lightboxIndex !== null && (e.key === "ArrowLeft" || e.key === "ArrowUp")) {
        showPrev();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, lightboxIndex, onClose, closeLightbox, showNext, showPrev]);

  // lock scrollu při otevření
  useEffect(() => {
    if (open) {
      setPage(1);
      setLightboxIndex(null);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center"
      aria-modal="true"
      role="dialog"
    >
      {/* backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => (lightboxIndex !== null ? closeLightbox() : onClose?.())}
      />

      {/* obsah modalu */}
      <div className="relative z-[1001] w-[min(1200px,95vw)] max-h:[90vh] max-h-[90vh] overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3 border-b">
          <h3 className="text-lg font-semibold">Fotogalerie</h3>
          <button
            onClick={onClose}
            className="rounded px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-sm"
          >
            Zavřít ✕
          </button>
        </div>

        <div className="p-4 overflow-auto max-h-[calc(90vh-56px)]">
          {/* GRID fotek */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {images.slice(0, totalShown).map((src, i) => (
              <button
                key={src + i}
                onClick={() => setLightboxIndex(i)}
                className="group relative block overflow-hidden rounded-lg border bg-white"
                title="Zvětšit"
              >
                <img
                  src={src}
                  alt={`foto-${i}`}
                  loading={i < 16 ? "eager" : "lazy"}
                  className="h-36 w-full object-cover transition-transform duration-200 group-hover:scale-[1.03]"
                />
                <div
                  className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{
                    background:
                      "linear-gradient(120deg, transparent 20%, rgba(255,255,255,.15) 40%, transparent 60%)",
                  }}
                />
              </button>
            ))}
          </div>

          {/* Load more */}
          {canLoadMore && (
            <div className="flex justify-center mt-4">
              <button
                onClick={() => setPage((p) => p + 1)}
                className="px-5 py-2 rounded bg-gray-900 text-white hover:bg-gray-800"
              >
                Načíst další
              </button>
            </div>
          )}
        </div>
      </div>

      {/* LIGHTBOX */}
      {lightboxIndex !== null && (
        <div className="absolute inset-0 z-[1002] flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/80"
            onClick={closeLightbox}
            aria-hidden="true"
          />
          <div className="relative z-[1003] max-w-[95vw] max-h-[90vh] flex items-center justify-center">
            <img
              src={images[lightboxIndex]}
              alt={`detail-${lightboxIndex}`}
              className="max-h-[90vh] max-w-[95vw] object-contain rounded-lg shadow-2xl"
            />

            {/* ovládací prvky */}
            <button
              onClick={showPrev}
              aria-label="Předchozí"
              className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full px-3 py-2 shadow"
            >
              ←
            </button>
            <button
              onClick={showNext}
              aria-label="Další"
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full px-3 py-2 shadow"
            >
              →
            </button>
            <button
              onClick={closeLightbox}
              aria-label="Zavřít"
              className="absolute top-2 right-2 bg-white/90 hover:bg-white rounded px-3 py-1.5 shadow"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
