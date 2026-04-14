import { setRequestLocale, getTranslations } from "next-intl/server";
import SectionTitle from "@/components/SectionTitle";

type Row = { doc: string; where: string };

export default async function Standards({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("standards");
  const rows = (t.raw("rows") as Row[]) ?? [];

  return (
    <div className="mx-auto max-w-7xl px-4 py-14">
      <SectionTitle title={t("h1")} sub={t("intro")} eyebrow="Standards & guidance" />

      <div className="panel ring-amber mb-6 px-4 py-3 text-[13px] text-amber">
        ⚠ {t("warning")}
      </div>

      <div className="panel overflow-x-auto">
        <table className="w-full border-collapse text-left text-[14px]">
          <thead className="border-b border-graphite-700/70 bg-navy-800/40">
            <tr>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-wider text-ink-400">
                Document
              </th>
              <th className="px-4 py-3 font-mono text-[11px] uppercase tracking-wider text-ink-400">
                Where it shows up
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => {
              const oos = r.where.includes("OUT OF SCOPE");
              return (
                <tr
                  key={i}
                  className="border-t border-graphite-700/40 hover:bg-graphite-800/30"
                >
                  <td className="whitespace-nowrap px-4 py-3 font-mono text-amber">
                    {r.doc}
                  </td>
                  <td className={`px-4 py-3 ${oos ? "text-ink-400 italic" : "text-ink-200"}`}>
                    {r.where}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-6 text-[13px] text-ink-400">{t("more")}</p>
    </div>
  );
}
