import React from "react";
import Hero from "./components/Hero.jsx";
import Products from "./components/Products.jsx";
import Pricing from "./components/Pricing.jsx";
import Gallery from "./components/Gallery.jsx";
import Liquidation from "./components/Liquidation";
import Location from "./components/Location.jsx";
import ContactForm from "./components/ContactForm.jsx";
import Footer from "./components/Footer.jsx";
import WhatsAppButton from "./components/WhatsAppButton.jsx";

export default function App() {
  return (
    <>
      <Hero />
      <main className="max-w-6xl mx-auto px-4">
        <Products />
        <Pricing />
        <Gallery />
        <Liquidation />
        <Location />
        <ContactForm />
      </main>
      <Footer />
      <WhatsAppButton />
    </>
  );
}
