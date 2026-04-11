import { MapPin, Truck } from "lucide-react";

const Lokalita = () => {
  return (
    <section id="lokalita" className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-14">
          <h2 className="font-display text-4xl sm:text-5xl text-foreground">
            Kde nás <span className="text-primary">najdete</span>
          </h2>
        </div>

        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8 items-center">
          <div className="space-y-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary shrink-0">
                <MapPin size={24} />
              </div>
              <div>
                <h3 className="font-display text-xl text-foreground">Adresa</h3>
                <p className="text-muted-foreground text-sm mt-1">
                  PVM Deal s.r.o.<br />
                  Polešovice<br />
                  687 37, okres Uherské Hradiště<br />
                  Česká republika
                </p>
                <a
                  href="https://maps.google.com/?q=Polešovice,+Uherské+Hradiště"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-2 text-primary text-sm hover:underline"
                >
                  Otevřít v Google Maps →
                </a>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary shrink-0">
                <Truck size={24} />
              </div>
              <div>
                <h3 className="font-display text-xl text-foreground">Doprava</h3>
                <p className="text-muted-foreground text-sm mt-1">
                  Zajistíme dopravu po celé České republice. Při větším
                  množství nabízíme dopravu zdarma. Možnost vlastního odběru
                  přímo ze skladu.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-lg overflow-hidden border border-border h-72">
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d10424.55!2d17.3505!3d48.9862!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47134b0e7a0e0001%3A0x400af0f6615c800!2sPole%C5%A1ovice!5e0!3m2!1scs!2scz!4v1700000000000!5m2!1scs!2scz"
              className="w-full h-full"
              style={{ border: 0, filter: "invert(0.9) hue-rotate(180deg) saturate(0.3)" }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              title="Mapa – Polešovice"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Lokalita;
