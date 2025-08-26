import React from "react";

export default function Footer() {
  return (
    <footer className="bg-gray-800 mt-12 text-gray-300">
      <div className="max-w-6xl mx-auto px-4 py-8 text-sm">
        <div className="flex flex-col md:flex-row justify-between gap-4">
          <div>
            <div className="font-semibold">
              Palety • Big-Bagy • Krabice • PVM-Deal.cz
            </div>
            <div>Polešovice 483, 68737 (u Uherského Hradiště)</div>
            <div>IČO: 75739593</div>
          </div>
          <div>
            <div>
              E-mail:{" "}
              <a
                className="underline hover:text-white"
                href="mailto:robin.strejcek@centrum.cz"
              >
                robin.strejcek@centrum.cz
              </a>
            </div>
            <div>
              Tel.:{" "}
              <a
                className="underline hover:text-white"
                href="tel:+420777863255"
              >
                +420 777 863 255
              </a>
            </div>
          </div>
        </div>
        <div className="mt-4 text-xs text-gray-500">
          © {new Date().getFullYear()} PVM-Deal.cz. Všechna práva vyhrazena.
        </div>
      </div>
    </footer>
  );
}
