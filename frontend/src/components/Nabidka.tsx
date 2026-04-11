import { Package, Container, Box } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const items = [
  {
    icon: Package,
    title: "Europalety",
    desc: "Prodej a výkup europalet (EUR, CP) všech kvalit. Nové, použité i opravené. Velkoobchodní i maloobchodní množství.",
    highlights: ["EUR 1200×800", "CP palety", "Atypické rozměry"],
  },
  {
    icon: Container,
    title: "Big-Bagy",
    desc: "Nové i použité big-bagy (FIBC). Ideální pro přepravu sypkých materiálů, zeminy, odpadu a dalšího.",
    highlights: ["Nové big-bagy", "Použité / jednou použité", "Různé nosnosti"],
  },
  {
    icon: Box,
    title: "Kartonové krabice",
    desc: "Nové i použité kartonové krabice různých rozměrů. Vhodné pro stěhování, skladování i zasílání zboží.",
    highlights: ["Stěhovací krabice", "Skladové krabice", "Klopové krabice"],
  },
];

const Nabidka = () => {
  return (
    <section id="nabidka" className="py-24 bg-secondary/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-14">
          <h2 className="font-display text-4xl sm:text-5xl text-foreground">
            Co <span className="text-primary">nabízíme</span>
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            Prodáváme a vykupujeme palety, big-bagy a krabice. Nabízíme
            konkurenční ceny a rychlé dodání.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {items.map((item) => (
            <Card
              key={item.title}
              className="group bg-card hover:border-primary/40 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-primary/5"
            >
              <CardContent className="p-8 space-y-4">
                <div className="w-14 h-14 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  <item.icon size={28} />
                </div>
                <h3 className="font-display text-2xl text-foreground">
                  {item.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {item.desc}
                </p>
                <ul className="space-y-1.5 pt-2">
                  {item.highlights.map((h) => (
                    <li
                      key={h}
                      className="flex items-center gap-2 text-sm text-foreground"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                      {h}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Nabidka;
