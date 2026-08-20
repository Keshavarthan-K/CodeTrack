const DIFFICULTY_META = {
  Easy: { color: "var(--accent)" },
  Medium: { color: "var(--accent-warm)" },
  Hard: { color: "var(--accent-danger)" },
  Unrated: { color: "var(--text-faint)" },
};

export default function DifficultyBars({ difficulty }) {
  const order = ["Easy", "Medium", "Hard", "Unrated"];
  const entries = order
    .filter((k) => difficulty[k])
    .map((k) => ({ key: k, count: difficulty[k], color: DIFFICULTY_META[k].color }));
  const total = entries.reduce((sum, e) => sum + e.count, 0) || 1;

  return (
    <div style={styles.wrap}>
      <div style={styles.title}>difficulty breakdown</div>

      <div style={styles.stackedBar}>
        {entries.map((e) => (
          <div
            key={e.key}
            style={{ width: `${(e.count / total) * 100}%`, background: e.color }}
            title={`${e.key}: ${e.count}`}
          />
        ))}
      </div>

      <div style={styles.legendRow}>
        {entries.map((e) => (
          <div key={e.key} style={styles.legendItem}>
            <span style={{ ...styles.dot, background: e.color }} />
            <span style={styles.legendLabel}>{e.key}</span>
            <span style={styles.legendCount}>{e.count}</span>
          </div>
        ))}
      </div>

      {entries.every((e) => e.key === "Unrated") && (
        <div style={styles.note}>
          Everything here is "Unrated" because these problems were synced before difficulty
          bucketing was added — re-run a sync to backfill it going forward.
        </div>
      )}
    </div>
  );
}

const styles = {
  wrap: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    padding: 20,
  },
  title: {
    fontFamily: "var(--font-mono)",
    fontSize: 12,
    color: "var(--text-secondary)",
    marginBottom: 16,
  },
  stackedBar: {
    display: "flex",
    height: 12,
    borderRadius: 6,
    overflow: "hidden",
    background: "var(--surface-raised)",
  },
  legendRow: { display: "flex", flexWrap: "wrap", gap: 16, marginTop: 16 },
  legendItem: { display: "flex", alignItems: "center", gap: 6 },
  dot: { width: 8, height: 8, borderRadius: "50%" },
  legendLabel: { fontSize: 13, color: "var(--text-primary)" },
  legendCount: { fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-secondary)" },
  note: {
    marginTop: 14,
    fontSize: 12,
    color: "var(--text-faint)",
    lineHeight: 1.5,
  },
};
