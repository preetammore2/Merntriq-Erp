import Image from "next/image";

export function BrandLogo({
  compact = false,
  className = "",
  size = "md",
}: {
  compact?: boolean;
  className?: string;
  size?: "md" | "lg";
}) {
  const boxSize = size === "lg" ? "h-16 w-16" : "h-10 w-10";
  const imageSize = size === "lg" ? 64 : 40;

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className={`flex ${boxSize} shrink-0 items-center justify-center overflow-hidden rounded-lg border border-line/70 bg-white p-1 shadow-sm`}>
        <Image
          src="/logo.png"
          alt="Mentriq360 logo"
          width={imageSize}
          height={imageSize}
          className="h-auto w-full object-contain"
          style={{ maxHeight: "100%" }}
          priority
        />
      </div>
      {!compact && (
        <div className="min-w-0">
          <p className="display-font truncate text-base font-semibold leading-tight text-ink">Mentriq360</p>
          <p className="truncate text-[11px] font-semibold uppercase tracking-[0.18em] text-muted">Campus ERP</p>
        </div>
      )}
    </div>
  );
}
