import { Link } from "@tanstack/react-router";

export function Footer() {
  return (
    <footer className="border-t border-border bg-muted/30">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-5 py-10 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
        <p>© {new Date().getFullYear()} ResumeIQ — AI Resume Analyzer & Job Match Platform.</p>
        <nav className="flex gap-5">
          <Link to="/" className="transition-colors hover:text-foreground">
            Home
          </Link>
          <Link to="/login" className="transition-colors hover:text-foreground">
            Login
          </Link>
          <Link to="/register" className="transition-colors hover:text-foreground">
            Get started
          </Link>
        </nav>
      </div>
    </footer>
  );
}
