export default function SectionTitle({
  eyebrow,
  title,
  sub,
}: {
  eyebrow?: string;
  title: string;
  sub?: string;
}) {
  return (
    <header className="mb-8">
      {eyebrow && <div className="label-mono mb-2">{eyebrow}</div>}
      <h1 className="text-3xl font-semibold tracking-tight text-ink-50 md:text-4xl">
        {title}
      </h1>
      {sub && <p className="mt-3 max-w-3xl text-ink-200">{sub}</p>}
    </header>
  );
}
