import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Phone, Mail, Send } from "lucide-react";
import { postContact } from "@/lib/api";

const Kontakt = () => {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const itemTypeRef = useRef<string>("");
  const [delivery, setDelivery] = useState(false);
  const [pickup, setPickup] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const form = e.currentTarget;
    const get = (id: string) => (form.elements.namedItem(id) as HTMLInputElement)?.value ?? "";

    try {
      await postContact({
        name: get("name"),
        email: get("email"),
        phone: get("phone"),
        itemType: itemTypeRef.current || "Neuvedeno",
        quantity: get("quantity"),
        location: get("location"),
        message: get("message"),
        delivery,
        pickup,
      });
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chyba při odesílání.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="kontakt" className="py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-14">
          <h2 className="font-display text-4xl sm:text-5xl text-foreground">
            Kontaktujte <span className="text-primary">nás</span>
          </h2>
          <p className="mt-3 text-muted-foreground max-w-xl mx-auto">
            Máte zájem o naše produkty nebo potřebujete individuální nabídku?
            Vyplňte formulář nebo nám zavolejte.
          </p>
        </div>

        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
          {/* Contact info */}
          <div className="space-y-6">
            <div className="flex items-start gap-3">
              <Phone size={20} className="text-primary mt-1 shrink-0" />
              <div>
                <p className="font-semibold text-foreground text-sm">Telefon</p>
                <a
                  href="tel:+420777863255"
                  className="text-muted-foreground text-sm hover:text-primary transition-colors"
                >
                  +420 777 863 255
                </a>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Mail size={20} className="text-primary mt-1 shrink-0" />
              <div>
                <p className="font-semibold text-foreground text-sm">E-mail</p>
                <a
                  href="mailto:robin.strejcek@centrum.cz"
                  className="text-muted-foreground text-sm hover:text-primary transition-colors"
                >
                  robin.strejcek@centrum.cz
                </a>
              </div>
            </div>

            <div className="pt-4 border-t border-border">
              <p className="text-sm text-muted-foreground">
                Odpovídáme zpravidla do 24 hodin v pracovní dny.
              </p>
            </div>
          </div>

          {/* Form */}
          <div className="md:col-span-2">
            {submitted ? (
              <div className="rounded-lg border border-primary/30 bg-primary/10 p-8 text-center space-y-2">
                <p className="font-display text-2xl text-primary">Děkujeme!</p>
                <p className="text-muted-foreground text-sm">
                  Vaši poptávku jsme přijali. Ozveme se vám co nejdříve.
                </p>
              </div>
            ) : (
              <form
                onSubmit={handleSubmit}
                className="space-y-4 bg-card rounded-lg border border-border p-6"
              >
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Jméno / Firma</Label>
                    <Input id="name" name="name" placeholder="Jan Novák" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">E-mail</Label>
                    <Input id="email" name="email" type="email" placeholder="jan@firma.cz" required />
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="phone">Telefon</Label>
                    <Input id="phone" name="phone" type="tel" placeholder="+420 ..." />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="type">Typ poptávky</Label>
                    <Select onValueChange={(val) => { itemTypeRef.current = val; }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Vyberte..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Palety">Palety</SelectItem>
                        <SelectItem value="Big-bagy">Big-bagy</SelectItem>
                        <SelectItem value="Krabice">Krabice</SelectItem>
                        <SelectItem value="Likvidace zásob">Likvidace zásob</SelectItem>
                        <SelectItem value="Jiné">Jiné</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="quantity">Množství</Label>
                    <Input id="quantity" name="quantity" placeholder="cca 100 ks" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">Lokalita</Label>
                    <Input id="location" name="location" placeholder="Brno, Zlín..." />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Zpráva</Label>
                  <Textarea
                    id="message"
                    name="message"
                    placeholder="Popište vaši poptávku..."
                    rows={4}
                    required
                  />
                </div>

                <div className="flex flex-wrap gap-6">
                  <div className="flex items-center gap-2">
                    <Checkbox id="dovoz" checked={delivery} onCheckedChange={(v) => setDelivery(!!v)} />
                    <Label htmlFor="dovoz" className="text-sm text-muted-foreground">
                      Mám zájem o dovoz
                    </Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Checkbox id="osobni" checked={pickup} onCheckedChange={(v) => setPickup(!!v)} />
                    <Label htmlFor="osobni" className="text-sm text-muted-foreground">
                      Osobní odběr
                    </Label>
                  </div>
                </div>

                {error && (
                  <p className="text-sm text-destructive">{error}</p>
                )}

                <Button type="submit" size="lg" className="w-full sm:w-auto" disabled={loading}>
                  <Send size={16} className="mr-2" />
                  {loading ? "Odesílám..." : "Odeslat poptávku"}
                </Button>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Kontakt;
