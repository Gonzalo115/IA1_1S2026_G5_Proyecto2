import "./ConfidenceBar.css";

interface Props {
  value: number;
}

export default function ConfidenceBar({ value }: Props) {
  const pct = Math.round(value * 100);
  const colorClass = pct >= 80 ? "bar-high" : pct >= 50 ? "bar-mid" : "bar-low";

  return (
    <div className="conf-bar">
      <div className="conf-bar-track">
        <div className={`conf-bar-fill ${colorClass}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`conf-bar-label conf-label-${colorClass}`}>{pct}%</span>
    </div>
  );
}
