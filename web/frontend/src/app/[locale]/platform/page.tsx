import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";
import ArchDiagram from "@/components/ArchDiagram";

export default async function Platform({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("platform");
  const why = (t.raw("why") as string[]) ?? [];
  const audience = (t.raw("audience") as string[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} />

      <div className="grid gap-6 md:grid-cols-2">
        <article className="panel p-6">
          <div className="label-mono mb-3">Layer 1</div>
          <h2 className="text-xl font-semibold">{t("layer_a_h")}</h2>
          <p className="mt-2 text-[14px] text-ink-200">{t("layer_a_body")}</p>
          <ul className="mt-4 space-y-1 text-[13px] text-ink-200">
            <li>• IMA-style scheduler · partition restart · cold/warm start</li>
            <li>• ARINC 429-lite + AFDX-lite (BAG / drop / delay / reorder)</li>
            <li>• FCC / Engine I/F / Display Computer / Data Concentrator</li>
            <li>• Requirement-based runner + line + MC/DC</li>
            <li>• Fault campaigns: detected / mitigated / escaped</li>
            <li>• Hermetic evidence bundle + sha256 + replay</li>
          </ul>
        </article>
        <article className="panel p-6 ring-amber">
          <div className="label-mono mb-3 text-amber">Layer 2</div>
          <h2 className="text-xl font-semibold">{t("layer_b_h")}</h2>
          <p className="mt-2 text-[14px] text-ink-200">{t("layer_b_body")}</p>
          <ul className="mt-4 space-y-1 text-[13px] text-ink-200">
            <li>• Phase A — Bronze/Silver/Gold lakehouse</li>
            <li>• Phase B — frozen learned components + registry</li>
            <li>• Phase C — GSN-lite assurance + reviewer workflow</li>
            <li>• Phase D — runtime assurance shell + Shadow → Advisory → LimSup</li>
            <li>• Phase E — portfolio packaging</li>
          </ul>
        </article>
      </div>

      <section className="mt-12">
        <div className="label-mono mb-3">{t("why_h")}</div>
        <ul className="space-y-2 text-[14px] text-ink-200">
          {why.map((w, i) => (
            <li key={i} className="panel px-4 py-3">{w}</li>
          ))}
        </ul>
      </section>

      <section className="mt-12">
        <ArchDiagram />
      </section>

      <section className="mt-12">
        <div className="label-mono mb-3">{t("audience_h")}</div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {audience.map((a, i) => (
            <div key={i} className="panel p-4 text-[13px] text-ink-200">{a}</div>
          ))}
        </div>
      </section>
    </div>
  );
}
