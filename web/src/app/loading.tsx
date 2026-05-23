import { BrandLogo } from "@/components/brand-logo";
import { Spinner } from "@/components/ui/spinner";

export default function Loading() {
  return (
    <main className="modern-shell flex min-h-screen items-center justify-center px-4">
      <div className="surface flex flex-col items-center gap-4 px-8 py-7">
        <BrandLogo />
        <Spinner size={28} className="text-teal-700" />
        <p className="text-sm text-muted">Loading workspace...</p>
      </div>
    </main>
  );
}
