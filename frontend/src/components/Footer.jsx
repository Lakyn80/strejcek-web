import React from "react";
export default function Footer() {
  return (
    <footer className="bg-gray-100 mt-12">
      <div className="max-w-6xl mx-auto px-4 py-8 text-sm text-gray-700">
        <div className="flex flex-col md:flex-row justify-between gap-4">
          <div>
            <div className="font-semibold">Palety • Big-Bagy • Krabice Strejček</div>
            <div>Polešovice u Uherského Hradiště</div>
            <div>IČO: 00000000 (placeholder)</div>
          </div>
          <div>
            <div>E-mail: <a className="underline" href="mailto:you@example.cz">you@example.cz</a></div>
            <div>Tel.: <a className="underline" href="tel:+420777000000">+420 777 000 000</a></div>
          </div>
        </div>
        <div className="mt-4 text-xs text-gray-500">
          © {new Date().getFullYear()} Palety • Big-Bagy • Krabice Strejček. Všechna práva vyhrazena.
        </div>
      </div>
    </footer>
  );
}
