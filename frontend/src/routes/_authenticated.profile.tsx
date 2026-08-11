import { useQuery } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { AlertCircle, LogOut } from "lucide-react";
import { toast } from "sonner";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { apiRequest } from "@/lib/api";
import { useAuth, type User } from "@/lib/auth";

export const Route = createFileRoute("/_authenticated/profile")({
  head: () => ({
    meta: [
      { title: "Profile — ResumeIQ" },
      { name: "description", content: "View your ResumeIQ account details and manage your session." },
      { property: "og:title", content: "Profile — ResumeIQ" },
      { property: "og:description", content: "Your ResumeIQ account details." },
    ],
  }),
  component: ProfilePage,
});

function ProfilePage() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const {
    data: profile,
    isPending,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: () => apiRequest<User>("/auth/me"),
  });

  async function handleLogout() {
    await logout();
    toast.success("Signed out");
    void navigate({ to: "/login", replace: true });
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-12">
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Profile</h1>
      <p className="mt-2 text-muted-foreground">Your account details.</p>

      <Card className="mt-8 border-border shadow-none">
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>Loaded from your ResumeIQ account.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {isPending ? (
            <div className="space-y-5">
              {Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="space-y-2">
                  <Skeleton className="h-3 w-24" />
                  <Skeleton className="h-5 w-56" />
                </div>
              ))}
            </div>
          ) : isError ? (
            <Alert variant="destructive">
              <AlertCircle className="size-4" />
              <AlertTitle>Couldn't load your profile</AlertTitle>
              <AlertDescription className="flex flex-col items-start gap-3">
                <span>{error instanceof Error ? error.message : "Unknown error"}</span>
                <Button size="sm" variant="outline" onClick={() => void refetch()}>
                  Try again
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <>
              <Field label="Name" value={profile.name} />
              <Separator />
              <Field label="Email" value={profile.email} />
              <Separator />
              <Field label="Member since" value={formatDate(profile.created_at)} />
            </>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6 border-border shadow-none">
        <CardHeader>
          <CardTitle>Session</CardTitle>
          <CardDescription>Sign out of this device.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={() => void handleLogout()}>
            <LogOut className="size-4" /> Log out
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1 text-foreground">{value}</p>
    </div>
  );
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}
