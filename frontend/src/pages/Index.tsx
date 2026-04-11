import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Nabidka from "@/components/Nabidka";
import Cenik from "@/components/Cenik";
import Galerie from "@/components/Galerie";
import Likvidace from "@/components/Likvidace";
import Lokalita from "@/components/Lokalita";
import Kontakt from "@/components/Kontakt";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <Nabidka />
      <Cenik />
      <Galerie />
      <Likvidace />
      <Lokalita />
      <Kontakt />
      <Footer />
    </div>
  );
};

export default Index;
