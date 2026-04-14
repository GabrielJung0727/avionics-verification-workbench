"use client";
import { useTranslations } from "next-intl";

export default function HardLineBanner() {
  const t = useTranslations("common");
  return (
    <div className="border-b border-amber/30 bg-amber/5 px-4 py-1.5 text-center text-[11px] font-mono uppercase tracking-wider text-amber">
      <span className="badge badge-amber mr-2">{t("hard_line_label")}</span>
      <span className="text-ink-200 normal-case tracking-normal">
        {t("draft_banner")}
      </span>
    </div>
  );
}
