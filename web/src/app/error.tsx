"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { BrandLogo } from "@/components/brand-logo";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="modern-shell flex min-h-screen items-center justify-center px-4 py-8">
      <section className="surface w-full max-w-lg p-6 text-center">
        <div className="flex justify-center">
          <BrandLogo />
        </div>
        <div className="mx-auto mt-6 flex h-12 w-12 items-center justify-center rounded-lg bg-rose-50 text-rose-700">
          <AlertTriangle size={22} />
        </div>
        <h1 className="display-font mt-4 text-2xl font-semibold text-ink">Something went wrong</h1>
        <p className="mt-2 text-sm leading-6 text-muted">
          The workspace could not render this view. Your session and data are protected; try loading the screen again.
        </p>
        <button
          type="button"
          onClick={reset}
          className="mx-auto mt-6 flex items-center gap-2 rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white shadow-sm"
        >
          <RefreshCcw size={14} />
          Reload view
        </button>
      </section>
    </main>
  );
}
