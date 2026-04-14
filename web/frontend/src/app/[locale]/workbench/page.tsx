import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";

type Stone = { id: string; h: string; body: string };

export default async function Workbench({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("workbench");
  const stones = (t.raw("stones") as Stone[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} eyebrow="M1 → M6" />

      <ol className="space-y-4">
        {stones.map((s, i) => (
          <li key={s.id} className="panel relative overflow-hidden p-5 md:p-6">
            <div className="absolute right-4 top-4 font-mono text-[11px] uppercase tracking-wider text-ink-400">
              {String(i + 1).padStart(2, "0")} / {String(stones.length).padStart(2, "0")}
            </div>
            <div className="flex items-baseline gap-3">
              <span className="badge badge-amber">{s.id}</span>
              <h2 className="text-lg font-semibold">{s.h}</h2>
            </div>
            <p className="mt-2 max-w-3xl text-[14px] text-ink-200">{s.body}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
