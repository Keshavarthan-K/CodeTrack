const stats = [
  { key: "total_solved", label: "total solved", accent: "var(--text-primary)" },
  { key: "today", label: "today", accent: "var(--accent)" },
  { key: "this_week", label: "this week", accent: "var(--accent)" },
  { key: "this_month", label: "this month", accent: "var(--accent)" },
  { key: "current_streak", label: "current streak", accent: "var(--accent-warm)", suffix: "d" },
  { key: "longest_streak", label: "longest streak", accent: "var(--accent-warm)", suffix: "d" },
];

export default function StatCards({ dashboard }) {
  return (
    <div style={styles.grid}>
      {stats.map((s) => (
        <div key={s.key} style={styles.card}>
          <div style={styles.label}>
            <span style={styles.chevron}>{">"}</span> {s.label}
          </div>
          <div style={{ ...styles.value, color: s.accent }}>
            {dashboard[s.key]}
            {s.suffix && <span style={styles.suffix}>{s.suffix}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}

const styles = {
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: 12,
  },
  card: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-md)",
    padding: "16px 18px",
  },
  label: {
    fontFamily: "var(--font-mono)",
    fontSize: 12,
    color: "var(--text-secondary)",
    marginBottom: 8,
    letterSpacing: 0.2,
  },
  chevron: { color: "var(--accent-dim)" },
  value: {
    fontFamily: "var(--font-display)",
    fontSize: 32,
    fontWeight: 600,
    lineHeight: 1,
  },
  suffix: {
    fontSize: 16,
    fontWeight: 500,
    marginLeft: 3,
    color: "var(--text-secondary)",
    fontFamily: "var(--font-mono)",
  },
};
