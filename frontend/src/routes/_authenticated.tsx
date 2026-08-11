import { Outlet, createFileRoute } from "@tanstack/react-router";

import { Footer } from "@/components/footer";
import { Navbar } from "@/components/navbar";
import { ProtectedRoute } from "@/components/protected-route";

export const Route = createFileRoute("/_authenticated")({
  component: AuthenticatedLayout,
});

function AuthenticatedLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />
      <main className="flex-1">
        <ProtectedRoute>
          <Outlet />
        </ProtectedRoute>
      </main>
      <Footer />
    </div>
  );
}
