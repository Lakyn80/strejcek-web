import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";

const benefits = [
  "Rychlý odvoz přebytečných zásob",
  "Výkup palet, big-bagů i krabic v jakémkoli stavu",
  "Ekologická likvidace a recyklace",
  "Flexibilní termíny dle vašich potřeb",
  "Doprava zajištěna po celé ČR",
  "Bezplatná cenová nabídka do 24 hodin",
];

const Likvidace = () => {
  return (
    <section id="likvidace" className="py-24">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h2 className="font-display text-4xl sm:text-5xl text-foreground">
              Likvidace <span className="text-primary">zásob</span>
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              Máte přebytečné palety, big-bagy nebo krabice? Zajistíme rychlý
              výkup nebo odvoz. Spolupracujeme s firmami po celé Moravě i
              Čechách.
            </p>
            <ul className="space-y-3">
              {benefits.map((b) => (
                <li key={b} className="flex items-start gap-3 text-foreground">
                  <CheckCircle
                    size={20}
                    className="text-primary mt-0.5 shrink-0"
                  />
                  <span className="text-sm">{b}</span>
                </li>
              ))}
            </ul>
            <Button size="lg" asChild>
              <a href="#kontakt">Odeslat poptávku na likvidaci</a>
            </Button>
          </div>

          <div className="relative">
            <div className="rounded-lg overflow-hidden border border-border shadow-2xl shadow-primary/10">
              <img
                src="/images/pvm-deal_webp_gallrey_imgs/Loading pallets into a delivery truck.png"
                alt="Nakládka a likvidace palet"
                className="w-full h-80 object-cover"
                loading="lazy"
              />
            </div>
            <div className="absolute -bottom-4 -left-4 w-24 h-24 border-l-4 border-b-4 border-primary rounded-bl-lg" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Likvidace;
