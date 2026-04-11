const Footer = () => {
  return (
    <footer className="border-t border-border bg-card py-10">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex flex-col items-center md:items-start gap-2">
            <img
              src="/PVM Deal lgo.png"
              alt="PVM-Deal logo"
              className="h-14 w-auto object-contain"
            />
            <p className="text-xs text-muted-foreground">
              Palety • Big-Bagy • Krabice
            </p>
          </div>

          <div className="text-center md:text-right text-xs text-muted-foreground space-y-1">
            <p>Robin Strejček · Polešovice 483, 687 37 · IČO: 75739593</p>
            <p>
              Tel:{" "}
              <a href="tel:+420777863255" className="hover:text-primary transition-colors">
                +420 777 863 255
              </a>{" "}
              · E-mail:{" "}
              <a href="mailto:robin.strejcek@centrum.cz" className="hover:text-primary transition-colors">
                robin.strejcek@centrum.cz
              </a>
            </p>
            <p>© {new Date().getFullYear()} PVM-Deal.cz Všechna práva vyhrazena.</p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
