import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";
import BackendStatus from "@/components/BackendStatus";
import LiveSummary from "@/components/LiveSummary";

type Row = { k: string; v: string };
type Group = { h: string; rows: Row[] };

export default async function Results({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("results");
  const tLive = await getTranslations("live");
  const groups = (t.raw("groups") as Group[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} eyebrow="Snapshot" />

      <section className="mb-10">
        <BackendStatus />
        <div className="mt-4">
          <div className="label-mono mb-2 text-cyan">
            {tLive("section_live_summary_h")}
          </div>
          <p className="mb-3 text-[13px] text-ink-400">
            {tLive("section_live_summary_sub")}
          </p>
          <LiveSummary />
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        {groups.map((g, i) => (
          <section key={i} className="panel p-5">
            <div className="label-mono mb-4 text-cyan">{g.h}</div>
            <dl className="divide-y divide-graphite-700/60">
              {g.rows.map((r, j) => (
                <div
                  key={j}
                  className="grid grid-cols-5 gap-3 py-2 text-[13px] md:text-[14px]"
                >
                  <dt className="col-span-2 text-ink-400">{r.k}</dt>
                  <dd className="col-span-3 font-mono text-ink-50">{r.v}</dd>
                </div>
              ))}
            </dl>
          </section>
        ))}
      </div>
    </div>
  );
}
