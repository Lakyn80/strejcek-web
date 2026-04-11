import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const prices = [
  { product: "Europaleta nová", buy: "—", sell: "od 250 Kč" },
  { product: "Europaleta použitá (I. jakost)", buy: "80–120 Kč", sell: "150–200 Kč" },
  { product: "Europaleta použitá (II. jakost)", buy: "40–70 Kč", sell: "80–130 Kč" },
  { product: "Europaleta na opravu", buy: "10–30 Kč", sell: "—" },
  { product: "CP paleta (různé typy)", buy: "dohodou", sell: "dohodou" },
  { product: "Big-bag nový", buy: "—", sell: "od 80 Kč" },
  { product: "Big-bag použitý", buy: "5–15 Kč", sell: "30–50 Kč" },
  { product: "Kartonová krabice (různé)", buy: "dohodou", sell: "od 15 Kč" },
];

const Cenik = () => {
  return (
    <section id="cenik" className="py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-14">
          <h2 className="font-display text-4xl sm:text-5xl text-foreground">
            Orientační <span className="text-primary">ceník</span>
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            Ceny jsou orientační a závisí na množství, kvalitě a aktuální
            situaci na trhu. Pro přesnou nabídku nás kontaktujte.
          </p>
        </div>

        <div className="max-w-3xl mx-auto rounded-lg border border-border overflow-hidden bg-card">
          <Table>
            <TableHeader>
              <TableRow className="bg-secondary/50 hover:bg-secondary/50">
                <TableHead className="text-foreground font-semibold">Produkt</TableHead>
                <TableHead className="text-foreground font-semibold text-center">Výkup</TableHead>
                <TableHead className="text-foreground font-semibold text-center">Prodej</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {prices.map((p, i) => (
                <TableRow key={i}>
                  <TableCell className="font-medium">{p.product}</TableCell>
                  <TableCell className="text-center text-muted-foreground">{p.buy}</TableCell>
                  <TableCell className="text-center text-primary font-semibold">{p.sell}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <p className="text-center text-sm text-muted-foreground mt-6 max-w-lg mx-auto">
          Při větším odběru poskytujeme objemové slevy. Doprava po dohodě –
          vlastní svoz nebo zajistíme dopravu po celé ČR.
        </p>
      </div>
    </section>
  );
};

export default Cenik;
