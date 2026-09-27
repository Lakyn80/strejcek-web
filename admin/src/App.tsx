import { FormEvent, useEffect, useMemo, useState } from "react";
import { LogIn, LogOut, ShieldCheck } from "lucide-react";

import {
  AccountingApp,
  AccountingConfigProvider,
  AccountingI18nProvider,
  configureAccountingHttp,
  type AccountingLocale,
  type AccountingUiConfig,
} from "@cz-accounting/accounting-ui";

import { adminFetch } from "./api";

const TOKEN_STORAGE_KEY = "strejcek.accountingAdminToken";

type LoginResponse = {
  access_token: string;
  expires_at: number;
  username: string;
  display_name: string;
  email: string | null;
};

type AdminPrincipal = {
  username: string;
  display_name: string;
  email: string | null;
  permissions: string[];
};

function readLocale(): AccountingLocale {
  const value = import.meta.env.VITE_ACCOUNTING_LOCALE;
  if (value === "en" || value === "ru" || value === "ua" || value === "cs") {
    return value;
  }
  return "cs";
}

function buildAccountingConfig(token: string): AccountingUiConfig {
  return {
    apiBaseUrl: import.meta.env.VITE_ACCOUNTING_API_URL ?? "",
    apiPrefix: import.meta.env.VITE_ACCOUNTING_API_PREFIX ?? "/api/accounting",
    appBaseRoute: import.meta.env.VITE_ACCOUNTING_APP_BASE_ROUTE ?? "/accounting",
    locale: readLocale(),
    authToken: token,
  };
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

function LoginScreen({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await adminFetch<LoginResponse>("/api/admin/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      onLogin(response.access_token);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Přihlášení selhalo.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-background px-4 py-10 text-foreground">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-lg border border-border bg-card p-6 shadow-xl shadow-black/20"
      >
        <div className="mb-6 flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-md bg-primary text-primary-foreground">
            <ShieldCheck className="size-5" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Accounting admin</h1>
            <p className="text-sm text-muted-foreground">PVM-Deal Strejček</p>
          </div>
        </div>

        <label className="block text-sm font-medium" htmlFor="username">
          Uživatelské jméno
        </label>
        <input
          id="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          className="mt-2 h-10 w-full rounded-md border border-input bg-background px-3 text-sm outline-none ring-offset-background transition focus:ring-2 focus:ring-ring"
          autoComplete="username"
          required
        />

        <label className="mt-4 block text-sm font-medium" htmlFor="password">
          Heslo
        </label>
        <input
          id="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mt-2 h-10 w-full rounded-md border border-input bg-background px-3 text-sm outline-none ring-offset-background transition focus:ring-2 focus:ring-ring"
          type="password"
          autoComplete="current-password"
          required
        />

        {error ? (
          <div className="mt-4 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        <button
          type="submit"
          className="mt-6 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isSubmitting}
        >
          <LogIn className="size-4" aria-hidden="true" />
          {isSubmitting ? "Přihlašuji..." : "Přihlásit"}
        </button>
      </form>
    </main>
  );
}

function LoadingScreen() {
  return (
    <main className="grid min-h-screen place-items-center bg-background px-4 text-sm text-muted-foreground">
      Načítám admin...
    </main>
  );
}

export function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY) ?? "");
  const [principal, setPrincipal] = useState<AdminPrincipal | null>(null);
  const [isChecking, setIsChecking] = useState(Boolean(token));

  const accountingConfig = useMemo(() => buildAccountingConfig(token), [token]);

  useEffect(() => {
    configureAccountingHttp(accountingConfig);
  }, [accountingConfig]);

  useEffect(() => {
    if (!token) {
      setPrincipal(null);
      setIsChecking(false);
      return;
    }

    let cancelled = false;
    setIsChecking(true);
    adminFetch<AdminPrincipal>("/api/admin/me", { headers: authHeaders(token) })
      .then((currentPrincipal) => {
        if (!cancelled) {
          setPrincipal(currentPrincipal);
        }
      })
      .catch(() => {
        if (!cancelled) {
          localStorage.removeItem(TOKEN_STORAGE_KEY);
          setToken("");
          setPrincipal(null);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsChecking(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  function handleLogin(nextToken: string) {
    localStorage.setItem(TOKEN_STORAGE_KEY, nextToken);
    setToken(nextToken);
    const baseRoute = accountingConfig.appBaseRoute || "/accounting";
    if (window.location.pathname !== baseRoute) {
      window.history.replaceState(null, "", baseRoute);
    }
  }

  async function handleLogout() {
    if (token) {
      await adminFetch("/api/admin/logout", {
        method: "POST",
        headers: authHeaders(token),
      }).catch(() => null);
    }
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken("");
    setPrincipal(null);
  }

  if (isChecking) {
    return <LoadingScreen />;
  }

  if (!token || !principal) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  return (
    <AccountingConfigProvider config={accountingConfig}>
      <AccountingI18nProvider language={accountingConfig.locale}>
        <div className="min-h-screen bg-background text-foreground">
          <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
            <div className="mx-auto flex min-h-14 max-w-7xl items-center justify-between gap-4 px-4">
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold">PVM-Deal Accounting</p>
                <p className="truncate text-xs text-muted-foreground">{principal.display_name}</p>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="inline-flex h-9 shrink-0 items-center justify-center gap-2 rounded-md border border-border bg-secondary px-3 text-sm text-secondary-foreground transition hover:bg-accent"
              >
                <LogOut className="size-4" aria-hidden="true" />
                Odhlásit
              </button>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-4 py-6">
            <AccountingApp />
          </main>
        </div>
      </AccountingI18nProvider>
    </AccountingConfigProvider>
  );
}
