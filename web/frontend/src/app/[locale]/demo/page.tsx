import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";

export default async function Demo({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("demo");
  const steps = (t.raw("steps") as string[]) ?? [];
  const artifacts = (t.raw("artifacts") as string[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} eyebrow="End-to-end" />

      <div className="panel grid-bg p-5 font-mono text-[13px] text-cyan md:text-[14px]">
        <span className="text-ink-400">$ </span>
        {t("cmd")}
      </div>

      <section className="mt-10">
        <div className="label-mono mb-4">{t("steps_h")}</div>
        <ol className="space-y-2">
          {steps.map((s, i) => (
            <li
              key={i}
              className="panel flex items-start gap-4 px-4 py-3 text-[14px]"
            >
              <span className="font-mono text-amber">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="text-ink-200">{s}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-10">
        <div className="label-mono mb-4">{t("artifacts_h")}</div>
        <ul className="space-y-2 text-[13px]">
          {artifacts.map((a, i) => (
            <li key={i} className="panel px-4 py-3 font-mono text-ink-200">
              {a}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
