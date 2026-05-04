type Stat = { label: string; value: string; desc: string };
type Dimension = { id: string; title: string; desc: string; accent: string };
type Preview = { rank: number; flag: string; country: string; score: number };
type Step = { n: number; title: string; desc: string };

const stats: Stat[] = [
  {
    label: "Países avaliados",
    value: "~190",
    desc: "Excluindo paraísos fiscais e estados não reconhecidos",
  },
  {
    label: "Fontes oficiais",
    value: "33",
    desc: "World Bank, Heritage, WIPO, IMF, OECD, UNDP…",
  },
  { label: "Dimensões", value: "4", desc: "TECH · VISA · PPP · MACRO" },
  {
    label: "Rankings prontos",
    value: "4",
    desc: "2 perfis × 2 modos pré-computados",
  },
];

const dimensions: Dimension[] = [
  {
    id: "TECH",
    title: "Mercado tech",
    desc: "Maturidade do ecossistema, salários para SWE, demanda e densidade de empresas.",
    accent: "badge-primary",
  },
  {
    id: "VISA",
    title: "Imigração",
    desc: "Vias realistas pra brasileiros: Digital Nomad, talento, work permit, ancestralidade.",
    accent: "badge-secondary",
  },
  {
    id: "PPP",
    title: "Custo de vida",
    desc: "Poder de compra real (PPP) descontando aluguel, alimentação e impostos.",
    accent: "badge-accent",
  },
  {
    id: "MACRO",
    title: "Estabilidade",
    desc: "Macro, governança e segurança. Gate redutor pra países instáveis.",
    accent: "badge-info",
  },
];

const previewTop5: Preview[] = [
  { rank: 1, flag: "🇨🇭", country: "Switzerland", score: 87.4 },
  { rank: 2, flag: "🇸🇬", country: "Singapore", score: 84.1 },
  { rank: 3, flag: "🇳🇱", country: "Netherlands", score: 81.2 },
  { rank: 4, flag: "🇩🇪", country: "Germany", score: 79.6 },
  { rank: 5, flag: "🇨🇦", country: "Canada", score: 78.9 },
];

const steps: Step[] = [
  {
    n: 1,
    title: "Coleta",
    desc: "Pipeline Python lê 33 fontes — APIs (World Bank, IMF), HTML scrape (Heritage via Wikipedia, WIPO via Datawrapper), planilhas oficiais.",
  },
  {
    n: 2,
    title: "Normaliza",
    desc: "Z-score global → clip ±3σ → escala 0–100. Imputação por mediana se cobertura ≥70%.",
  },
  {
    n: 3,
    title: "Aplica gates",
    desc: "VISA = 0 sem visto viável. MACRO < 25 → ×0,7. MACRO < 15 → ×0,4. Sem aceno pra países sem caminho real.",
  },
  {
    n: 4,
    title: "Rankeia",
    desc: "Pesos editáveis no browser. 4 dimensões reativas. Resposta instantânea, zero backend.",
  },
];

const ArrowRight = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M5 12h14M13 6l6 6-6 6" />
  </svg>
);

export default function Home() {
  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="from-primary/10 via-base-100 to-secondary/5 absolute inset-0 -z-10 bg-linear-to-br" />
        <div className="hero min-h-[80vh]">
          <div className="hero-content flex-col gap-12 px-4 lg:flex-row lg:gap-16">
            <div className="max-w-2xl">
              <div className="badge badge-primary badge-soft mb-6 gap-2">
                <span className="status status-primary" />
                versão pré-MVP · dados em validação
              </div>
              <h1 className="text-5xl leading-[1.05] font-black tracking-tight text-balance lg:text-7xl">
                Pra qual país <span className="text-primary">você deveria</span>
                <br />
                mirar?
              </h1>
              <p className="text-base-content/70 mt-6 max-w-xl text-lg lg:text-xl">
                Ranking objetivo de ~190 países pela viabilidade de imigração
                de um{" "}
                <span className="text-base-content font-semibold">
                  software engineer brasileiro
                </span>{" "}
                pleno→senior. Dados públicos, gates explícitos, pesos
                editáveis no cliente.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a href="/ranking" className="btn btn-primary btn-lg">
                  Ver ranking <ArrowRight />
                </a>
                <a href="#how" className="btn btn-ghost btn-lg">
                  Como funciona
                </a>
              </div>
            </div>

            <div className="w-full max-w-md">
              <div className="mockup-window border-base-300 bg-base-200 border shadow-2xl">
                <div className="bg-base-100 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="font-bold">Top 5 — preview</h3>
                    <span className="badge badge-ghost text-xs">
                      senior · local
                    </span>
                  </div>
                  <ul className="space-y-1.5">
                    {previewTop5.map((p) => (
                      <li
                        key={p.rank}
                        className="hover:bg-base-200 flex items-center gap-3 rounded-lg p-2 transition-colors"
                      >
                        <span className="text-base-content/40 w-6 font-mono text-sm">
                          #{p.rank}
                        </span>
                        <span className="text-2xl leading-none">{p.flag}</span>
                        <span className="flex-1 font-medium">{p.country}</span>
                        <span className="text-primary font-mono font-bold">
                          {p.score}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <p className="text-base-content/50 mt-4 text-xs">
                    Valores ilustrativos — pipeline em validação.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* STATS */}
      <section className="container mx-auto px-4 py-12 lg:py-16">
        <div className="stats stats-vertical lg:stats-horizontal bg-base-200 w-full shadow-sm">
          {stats.map((s) => (
            <div key={s.label} className="stat">
              <div className="stat-title">{s.label}</div>
              <div className="stat-value text-primary">{s.value}</div>
              <div className="stat-desc text-balance">{s.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* DIMENSOES */}
      <section className="container mx-auto px-4 py-12 lg:py-20">
        <div className="mb-10 max-w-2xl">
          <h2 className="text-4xl font-black tracking-tight lg:text-5xl">
            As 4 dimensões
          </h2>
          <p className="text-base-content/70 mt-3 text-lg">
            Sem hierarquia fixa. Você escolhe o peso de cada uma — ranking
            recalcula sem recarregar.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {dimensions.map((d) => (
            <div
              key={d.id}
              className="card bg-base-100 border-base-300 border transition-shadow hover:shadow-lg"
            >
              <div className="card-body">
                <span
                  className={`badge ${d.accent} badge-soft mb-2 self-start font-mono`}
                >
                  {d.id}
                </span>
                <h3 className="card-title">{d.title}</h3>
                <p className="text-base-content/70 text-sm">{d.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* COMO FUNCIONA */}
      <section id="how" className="container mx-auto px-4 py-12 lg:py-20">
        <div className="mb-10 max-w-2xl">
          <h2 className="text-4xl font-black tracking-tight lg:text-5xl">
            Como funciona
          </h2>
          <p className="text-base-content/70 mt-3 text-lg">
            Pipeline determinístico em quatro passos. Sem mágica, sem ML, sem
            opinião.
          </p>
        </div>
        <ul className="timeline timeline-vertical lg:timeline-horizontal w-full">
          {steps.map((s, i) => (
            <li key={s.n}>
              {i > 0 && <hr className="bg-primary/30" />}
              <div className="timeline-middle">
                <div className="bg-primary text-primary-content grid h-9 w-9 place-items-center rounded-full font-bold shadow">
                  {s.n}
                </div>
              </div>
              <div className="timeline-end timeline-box bg-base-100 border-base-300 max-w-xs border">
                <h4 className="font-bold">{s.title}</h4>
                <p className="text-base-content/70 mt-1 text-sm">{s.desc}</p>
              </div>
              {i < steps.length - 1 && <hr className="bg-primary/30" />}
            </li>
          ))}
        </ul>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16 lg:py-24">
        <div className="hero from-primary/10 via-base-200 to-secondary/10 rounded-3xl bg-linear-to-br">
          <div className="hero-content py-16 text-center">
            <div>
              <h2 className="text-4xl font-black tracking-tight lg:text-5xl">
                Pronto pra ver onde você está?
              </h2>
              <p className="text-base-content/70 mx-auto mt-4 max-w-xl text-lg">
                Brasil entra como calibração. Você ajusta os pesos, o ranking
                responde.
              </p>
              <a href="/ranking" className="btn btn-primary btn-lg mt-8">
                Abrir ranking <ArrowRight />
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
