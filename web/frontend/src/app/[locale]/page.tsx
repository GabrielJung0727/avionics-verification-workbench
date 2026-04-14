import { setRequestLocale, getTranslations } from "next-intl/server";
import { Link } from "@/i18n/routing";
import ArchDiagram from "@/components/ArchDiagram";
import MetricCard from "@/components/MetricCard";

export default async function Home({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("home");
  const tCommon = await getTranslations("common");
  const cards = (t.raw("cards") as { title: string; body: string }[]) ?? [];
  const does = (t.raw("does") as string[]) ?? [];
  const doesnt = (t.raw("doesnt") as string[]) ?? [];

  return (
    <>
      {/* Hero */}
      <section className="border-b border-graphite-700/60 grid-bg">
        <div className="mx-auto max-w-7xl px-4 py-20 md:py-28">
          <div className="label-mono mb-3">{t("hero_eyebrow")}</div>
          <h1 className="max-w-4xl text-4xl font-semibold leading-tight tracking-tight md:text-5xl">
            {t("hero_h1")}
          </h1>
          <p className="mt-5 max-w-3xl text-ink-200">{t("hero_sub")}</p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/platform" className="badge badge-amber">
              {t("cta_arch")}
            </Link>
            <Link href="/demo" className="badge badge-cyan">
              {t("cta_demo")}
            </Link>
            <Link href="/docs" className="badge">
              {t("cta_docs")}
            </Link>
          </div>
        </div>
      </section>

      {/* Pillars */}
      <section className="mx-auto max-w-7xl px-4 py-16">
        <div className="label-mono mb-6">{t("cards_h")}</div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {cards.map((c, i) => (
            <article key={i} className="panel p-5">
              <div className="text-[12px] font-mono text-amber">{`0${i + 1}`}</div>
              <h3 className="mt-1 text-lg font-semibold text-ink-50">{c.title}</h3>
              <p className="mt-2 text-[14px] text-ink-200">{c.body}</p>
            </article>
          ))}
        </div>
      </section>

      {/* What it does / does NOT */}
      <section className="border-y border-graphite-700/60 bg-navy-950/40">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-14 md:grid-cols-2">
          <div className="panel p-6">
            <div className="label-mono mb-3 text-cyan">{t("does_h")}</div>
            <ul className="space-y-2 text-[14px]">
              {does.map((d, i) => (
                <li key={i} className="flex gap-3">
                  <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-cyan" />
                  {d}
                </li>
              ))}
            </ul>
          </div>
          <div className="panel p-6 ring-amber">
            <div className="label-mono mb-3 text-amber">{t("doesnt_h")}</div>
            <ul className="space-y-2 text-[14px]">
              {doesnt.map((d, i) => (
                <li key={i} className="flex gap-3">
                  <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-amber" />
                  {d}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Metrics */}
      <section className="mx-auto max-w-7xl px-4 py-14">
        <div className="label-mono mb-4">{t("metrics_h")}</div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Total tests" value="174 / 174" tone="ok" />
          <MetricCard label="MC/DC" value="100%" tone="amber" hint="2 designated decisions" />
          <MetricCard label="HF evaluators" value="6 / 6" tone="cyan" />
          <MetricCard label="HIL configs" value="4" hint="nominal · latency · drop · reboot" />
          <MetricCard label="Frozen models" value="3" hint="escape · anomaly · trace gap" />
          <MetricCard label="Assurance cases" value="3 / 3" tone="ok" />
          <MetricCard label="Lakehouse Silver tables" value="9" />
          <MetricCard label="Evidence bundles" value="immutable + sha256 replay" />
        </div>
      </section>

      {/* Architecture */}
      <section className="mx-auto max-w-7xl px-4 pb-20">
        <ArchDiagram caption={t("arch_caption")} />
        <p className="mt-4 text-center text-[12px] text-ink-400">
          {tCommon("draft_banner")}
        </p>
      </section>
    </>
  );
}
