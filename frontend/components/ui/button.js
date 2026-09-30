"use client";

// Minimal button matching the design's variants (default / ghost / outline)
// and sizes (default / sm / icon). Icons are lucide-react SVGs sized here.
const VARIANTS = {
  default: "bg-primary text-primary-foreground hover:opacity-90",
  ghost: "text-foreground hover:bg-raised",
  outline: "border border-border bg-panel text-foreground hover:bg-raised",
};

const SIZES = {
  default: "h-8 px-3 text-xs",
  sm: "h-7 px-2.5 text-[11px]",
  icon: "h-8 w-8",
};

export function Button({
  variant = "default",
  size = "default",
  className = "",
  children,
  ...props
}) {
  const classes = [
    "inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors",
    "disabled:opacity-50 disabled:pointer-events-none [&_svg]:size-3.5 [&_svg]:shrink-0",
    VARIANTS[variant] || VARIANTS.default,
    SIZES[size] || SIZES.default,
    className,
  ].join(" ");
  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}

export default Button;
