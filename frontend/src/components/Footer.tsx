const FACEBOOK_URL = "https://www.facebook.com/pvmdeal";
const WHATSAPP_URL = "https://wa.me/420777863255";

const Footer = () => {
  return (
    <footer className="border-t border-border bg-card py-10">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo + socials */}
          <div className="flex flex-col items-center md:items-start gap-3">
            <img
              src="/PVM%20Deal%20lgo.png"
              alt="PVM-Deal logo"
              className="h-14 w-auto object-contain"
            />
            <p className="text-xs text-muted-foreground">
              Palety • Big-Bagy • Krabice
            </p>
            {/* Social icons */}
            <div className="flex items-center gap-3">
              <a
                href={WHATSAPP_URL}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="WhatsApp"
                className="flex items-center justify-center w-8 h-8 rounded-full transition-opacity hover:opacity-80"
                style={{ backgroundColor: "#25D366" }}
              >
                <svg viewBox="0 0 32 32" fill="white" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
                  <path d="M16 2C8.268 2 2 8.268 2 16c0 2.49.648 4.829 1.781 6.86L2 30l7.347-1.757A13.934 13.934 0 0 0 16 30c7.732 0 14-6.268 14-14S23.732 2 16 2zm0 25.5a11.44 11.44 0 0 1-5.826-1.594l-.418-.248-4.36 1.043 1.074-4.252-.272-.437A11.46 11.46 0 0 1 4.5 16C4.5 9.649 9.649 4.5 16 4.5S27.5 9.649 27.5 16 22.351 27.5 16 27.5zm6.29-8.465c-.345-.173-2.04-1.006-2.356-1.12-.316-.115-.546-.173-.776.173-.23.345-.89 1.12-1.09 1.35-.2.23-.4.26-.745.087-.345-.173-1.456-.537-2.773-1.71-1.025-.913-1.717-2.04-1.918-2.385-.2-.345-.021-.532.15-.704.155-.155.345-.404.518-.605.172-.202.23-.345.345-.575.115-.23.058-.432-.029-.605-.087-.173-.776-1.87-1.063-2.562-.28-.672-.564-.58-.776-.591l-.661-.012c-.23 0-.604.087-.92.432-.316.346-1.205 1.178-1.205 2.872s1.234 3.33 1.406 3.56c.173.23 2.43 3.71 5.888 5.204.823.355 1.465.567 1.965.726.826.263 1.578.226 2.172.137.663-.099 2.04-.833 2.328-1.637.287-.805.287-1.495.2-1.638-.086-.143-.316-.23-.661-.403z"/>
                </svg>
              </a>
              <a
                href={FACEBOOK_URL}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Facebook"
                className="flex items-center justify-center w-8 h-8 rounded-full transition-opacity hover:opacity-80"
                style={{ backgroundColor: "#1877F2" }}
              >
                <svg viewBox="0 0 24 24" fill="white" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
                  <path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Contact info */}
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
            <p>
              Web vytvořil{" "}
              <a
                href="https://lukiora.com"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
              >
                lukiora.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
