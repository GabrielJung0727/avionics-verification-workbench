import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";
import LiveModels from "@/components/LiveModels";
import BackendStatus from "@/components/BackendStatus";

type Phase = { id: string; h: string; body: string };

export default async function Intelligence({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("intelligence");
  const tLive = await getTranslations("live");
  const phases = (t.raw("phases") as Phase[]) ?? [];
  const hardline = (t.raw("hardline") as string[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} eyebrow="Phase A → E" />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {phases.map((p) => (
          <article key={p.id} className="panel p-5">
            <div className="badge badge-cyan w-fit">{p.id}</div>
            <h3 className="mt-3 text-base font-semibold">{p.h}</h3>
            <p className="mt-2 text-[13px] leading-relaxed text-ink-200">{p.body}</p>
          </article>
        ))}
      </div>

      <section className="mt-12 panel ring-amber p-6">
        <div className="label-mono text-amber">{t("hardline_h")}</div>
        <ul className="mt-3 grid gap-2 md:grid-cols-2">
          {hardline.map((h, i) => (
            <li key={i} className="flex gap-3 text-[14px]">
              <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-amber" />
              {h}
            </li>
          ))}
        </ul>
      </section>

      {/* Live registry */}
      <section className="mt-12">
        <div className="mb-4">
          <BackendStatus />
        </div>
        <div className="label-mono mb-2 text-cyan">
          {tLive("section_live_models_h")}
        </div>
        <p className="mb-4 text-[13px] text-ink-400">
          {tLive("section_live_models_sub")}
        </p>
        <LiveModels />
      </section>
    </div>
  );
}
