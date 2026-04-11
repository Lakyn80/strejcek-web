import { Button } from "@/components/ui/button";
import { ArrowDown } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative min-h-screen flex items-center pt-16 overflow-hidden">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-secondary/40" />

      {/* Accent glow */}
      <div className="absolute -top-32 -right-32 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />

      <div className="container mx-auto px-4 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Text */}
          <div className="space-y-6">
            <div className="inline-block px-4 py-1.5 rounded-full border border-primary/30 bg-primary/10 text-primary text-sm font-medium">
              Polešovice u Uherského Hradiště
            </div>

            <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl leading-[0.95] text-foreground">
              Palety{" "}
              <span className="text-primary">•</span> Big-Bagy{" "}
              <span className="text-primary">•</span> Krabice
            </h1>

            <p className="text-lg text-muted-foreground max-w-lg leading-relaxed">
              Prodej a výkup europalet, big-bagů a kartonových krabic. Spolehlivý
              partner pro váš byznys s rychlým dodáním po celé Moravě.
            </p>

            <div className="flex flex-wrap gap-3 pt-2">
              <Button size="lg" asChild>
                <a href="#nabidka">Nabídka</a>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <a href="#cenik">Orientační ceník</a>
              </Button>
              <Button size="lg" variant="ghost" asChild>
                <a href="#kontakt">
                  Kontakt <ArrowDown className="ml-1" size={16} />
                </a>
              </Button>
            </div>
          </div>

          {/* Image grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2 rounded-lg overflow-hidden border border-border shadow-2xl shadow-primary/5">
              <img
                src="/images/palety_5.webp"
                alt="Sklad palet PVM Deal"
                className="w-full h-56 object-cover"
                loading="eager"
              />
            </div>
            <div className="rounded-lg overflow-hidden border border-border">
              <img
                src="/images/bagy_2.webp"
                alt="Big-bagy"
                className="w-full h-36 object-cover"
                loading="eager"
              />
            </div>
            <div className="rounded-lg overflow-hidden border border-border">
              <img
                src="/images/krab_3.webp"
                alt="Krabice"
                className="w-full h-36 object-cover"
                loading="eager"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
