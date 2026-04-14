"use client";

import { useTranslations, useLocale } from "next-intl";
import { Link, usePathname } from "@/i18n/routing";
import BackendStatus from "./BackendStatus";

const ITEMS = [
  { key: "home", href: "/" as const },
  { key: "platform", href: "/platform" as const },
  { key: "workbench", href: "/workbench" as const },
  { key: "intelligence", href: "/intelligence" as const },
  { key: "demo", href: "/demo" as const },
  { key: "standards", href: "/standards" as const },
  { key: "docs", href: "/docs" as const },
  { key: "results", href: "/results" as const },
  { key: "about", href: "/about" as const },
] as const;

export default function Nav() {
  const t = useTranslations("nav");
  const tSite = useTranslations("site");
  const pathname = usePathname();
  const locale = useLocale();
  const otherLocale = locale === "ko" ? "en" : "ko";

  return (
    <header className="sticky top-0 z-30 border-b border-graphite-700/70 bg-navy-900/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3">
        <Link
          href="/"
          className="flex items-center gap-2 font-mono text-[13px] uppercase tracking-wider text-amber"
        >
          <span className="inline-block h-2 w-2 rounded-full bg-amber" />
          AVX
        </Link>
        <span className="hidden text-[11px] font-mono uppercase tracking-wider text-ink-400 lg:inline">
          {tSite("title")}
        </span>

        <nav className="ml-auto hidden flex-wrap items-center gap-x-5 gap-y-1 text-[13px] md:flex">
          {ITEMS.map((it) => {
            const active =
              it.href === "/"
                ? pathname === "/"
                : pathname.startsWith(it.href);
            return (
              <Link
                key={it.key}
                href={it.href}
                className={
                  "transition-colors hover:text-amber " +
                  (active ? "text-amber" : "text-ink-200")
                }
              >
                {t(it.key)}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <BackendStatus compact />
          <Link
            href={pathname as any}
            locale={otherLocale as "ko" | "en"}
            className="badge"
            aria-label={t("lang_label")}
          >
            {otherLocale.toUpperCase()}
          </Link>
        </div>
      </div>

      <nav className="md:hidden border-t border-graphite-700/70 px-4 pb-2 pt-1">
        <ul className="flex flex-wrap gap-x-4 gap-y-1 text-[12px] text-ink-200">
          {ITEMS.map((it) => (
            <li key={it.key}>
              <Link href={it.href} className="hover:text-amber">
                {t(it.key)}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
