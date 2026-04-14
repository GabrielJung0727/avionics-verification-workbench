import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";

type Item = { title: string; href: string };
type Cat = { h: string; items: Item[] };

export default async function Docs({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("docs");
  const categories = (t.raw("categories") as Cat[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} eyebrow="Documentation hub" />

      <div className="grid gap-6 md:grid-cols-2">
        {categories.map((c, i) => (
          <section key={i} className="panel p-5">
            <div className="label-mono mb-3 text-cyan">{c.h}</div>
            <ul className="space-y-2 text-[14px]">
              {c.items.map((it, j) => (
                <li key={j}>
                  <a
                    href={it.href}
                    target="_blank"
                    rel="noreferrer"
                    className="group flex items-baseline gap-2 hover:text-amber"
                  >
                    <span className="font-mono text-[11px] text-ink-400 group-hover:text-amber">
                      ↗
                    </span>
                    <span>{it.title}</span>
                  </a>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
