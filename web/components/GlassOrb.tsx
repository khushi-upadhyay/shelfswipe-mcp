export default function GlassOrb({ size = 52 }: { size?: number }) {
  return (
    <div
      style={{ width: size, height: size }}
      className="glass-sphere"
      aria-hidden="true"
    />
  );
}

