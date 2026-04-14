"use client";
import { useTranslations } from "next-intl";

const REPO = "https://github.com/GabrielJung0727/avionics-verification-workbench";
const GLAB = "https://gitlab.com/GabrielJung0727/avionics-verification-workbench";
const WIKI = "https://gitlab.com/GabrielJung0727/avionics-verification-workbench/-/wikis/home";

export default function Footer() {
  const t = useTranslations("site");
  return (
    <footer className="mt-24 border-t border-graphite-700/70 bg-navy-950/60">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-8 md:flex-row md:items-center md:justify-between">
        <div className="text-[12px] text-ink-400">
          © {new Date().getFullYear()} {t("owner")} · MIT licensed
        </div>
        <ul className="flex gap-4 text-[12px]">
          <li>
            <a href={REPO} className="hover:text-amber" target="_blank" rel="noreferrer">
              {t("github")}
            </a>
          </li>
          <li>
            <a href={GLAB} className="hover:text-amber" target="_blank" rel="noreferrer">
              {t("gitlab")}
            </a>
          </li>
          <li>
            <a href={WIKI} className="hover:text-amber" target="_blank" rel="noreferrer">
              {t("wiki")}
            </a>
          </li>
        </ul>
      </div>
    </footer>
  );
}
