import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";

export default async function About({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("about");
  const fit = (t.raw("fit") as string[]) ?? [];
  const contact = (t.raw("contact") as { k: string; v: string }[]) ?? [];

  return (
    <div className="mx-auto max-w-5xl px-4 py-14">
      <SectionTitle title={t("h1")} eyebrow="About" />

      <section className="panel p-6">
        <div className="label-mono mb-3 text-cyan">{t("intent_h")}</div>
        <p className="text-[14px] text-ink-200">{t("intent")}</p>
      </section>

      <section className="mt-6 panel p-6">
        <div className="label-mono mb-3 text-cyan">{t("fit_h")}</div>
        <ul className="grid gap-2 sm:grid-cols-2">
          {fit.map((f, i) => (
            <li
              key={i}
              className="rounded-sm border border-graphite-700 bg-navy-800/40 px-3 py-2 text-[13px]"
            >
              {f}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-6 panel p-6">
        <div className="label-mono mb-3 text-cyan">{t("contact_h")}</div>
        <dl className="divide-y divide-graphite-700/60">
          {contact.map((c, i) => (
            <div key={i} className="flex flex-col gap-1 py-3 sm:flex-row sm:items-baseline sm:gap-6">
              <dt className="w-32 text-ink-400">{c.k}</dt>
              <dd className="font-mono text-[13px]">
                <a
                  href={c.v}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-amber"
                >
                  {c.v}
                </a>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="mt-6 panel ring-amber p-6">
        <div className="label-mono mb-3 text-amber">{t("disclaimer_h")}</div>
        <p className="text-[14px] text-ink-200">{t("disclaimer")}</p>
      </section>
    </div>
  );
}
