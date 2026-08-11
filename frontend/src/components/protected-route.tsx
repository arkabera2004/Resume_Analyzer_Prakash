import { useNavigate, useRouterState } from "@tanstack/react-router";
import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/lib/auth";

/**
 * Client-side gate for routes that require a JWT session.
 * Unauthenticated visitors are sent to /login with the intended path preserved.
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const href = useRouterState({ select: (state) => state.location.href });

  // The destination is captured once so the redirect never chains onto itself.
  const intendedHref = useRef(href);
  const hasRedirected = useRef(false);

  useEffect(() => {
    if (isLoading || isAuthenticated || hasRedirected.current) return;
    hasRedirected.current = true;
    void navigate({ to: "/login", search: { redirect: intendedHref.current }, replace: true });
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading || !isAuthenticated) {
    return (
      <div className="mx-auto w-full max-w-6xl space-y-4 px-5 py-16">
        <Skeleton className="h-9 w-56" />
        <Skeleton className="h-4 w-80" />
        <div className="grid gap-4 pt-6 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-28 w-full" />
          ))}
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
