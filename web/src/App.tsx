import { ThemeToggle } from "./components/ThemeToggle";
import Home from "./pages/Home";

export default function App() {
  return (
    <div className="bg-base-100 text-base-content flex min-h-screen flex-col">
      <header className="navbar bg-base-100/80 border-base-300 sticky top-0 z-30 border-b backdrop-blur">
        <div className="navbar-start">
          <a href="/" className="btn btn-ghost gap-2 text-lg lg:text-xl">
            <span className="bg-primary text-primary-content grid h-8 w-8 place-items-center rounded-md">
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
                <circle cx="12" cy="12" r="10" />
                <path d="M2 12h20" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
            </span>
            <span>WorldRanking</span>
          </a>
        </div>

        <nav className="navbar-center hidden md:flex">
          <ul className="menu menu-horizontal gap-1 px-1">
            <li>
              <a href="/">Home</a>
            </li>
            <li>
              <a href="/ranking">Ranking</a>
            </li>
            <li>
              <a href="#how">Metodologia</a>
            </li>
          </ul>
        </nav>

        <div className="navbar-end gap-1">
          <a
            href="https://github.com/rodniski/world-ranking"
            className="btn btn-ghost btn-sm hidden sm:inline-flex"
            target="_blank"
            rel="noopener"
          >
            GitHub
          </a>
          <ThemeToggle />
        </div>
      </header>

      <main className="flex-1">
        <Home />
      </main>

      <footer className="footer footer-horizontal border-base-300 bg-base-200 text-base-content/70 border-t p-10">
        <aside className="max-w-md">
          <p className="text-sm">
            <strong className="text-base-content">WorldRanking</strong> —
            pesquisa pessoal, pré-MVP.
            <br />
            Dados públicos: World Bank, Heritage, WIPO, IMF, OECD, UNDP e +30
            fontes.
          </p>
        </aside>
        <nav>
          <h6 className="footer-title">Projeto</h6>
          <a
            href="https://github.com/rodniski/world-ranking"
            className="link link-hover"
            target="_blank"
            rel="noopener"
          >
            GitHub
          </a>
          <a href="#how" className="link link-hover">
            Metodologia
          </a>
          <a href="/ranking" className="link link-hover">
            Ranking
          </a>
        </nav>
      </footer>
    </div>
  );
}
