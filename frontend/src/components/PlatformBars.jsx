const PLATFORM_META = {
  codeforces: { label: "Codeforces", color: "var(--platform-codeforces)" },
  leetcode: { label: "LeetCode", color: "var(--platform-leetcode)" },
  codechef: { label: "CodeChef", color: "var(--platform-codechef)" },
};

export default function PlatformBars({ platforms }) {
  const entries = Object.entries(PLATFORM_META).map(([key, meta]) => ({
    key,
    ...meta,
    count: platforms[key] || 0,
  }));
  const max = Math.max(1, ...entries.map((e) => e.count));

  return (
    <div style={styles.wrap}>
      <div style={styles.title}>platform breakdown</div>
      <div style={styles.rows}>
        {entries.map((e) => (
          <div key={e.key} style={styles.row}>
            <div style={styles.rowLabel}>{e.label}</div>
            <div style={styles.barTrack}>
              <div
                style={{
                  ...styles.barFill,
                  width: `${(e.count / max) * 100}%`,
                  background: e.color,
                }}
              />
            </div>
            <div style={styles.rowCount}>{e.count}</div>
          </div>
        ))}
      </div>
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
    marginBottom: 18,
  },
  rows: { display: "flex", flexDirection: "column", gap: 14 },
  row: { display: "grid", gridTemplateColumns: "88px 1fr 44px", alignItems: "center", gap: 12 },
  rowLabel: { fontSize: 13, color: "var(--text-primary)", fontWeight: 500 },
  barTrack: {
    height: 10,
    background: "var(--surface-raised)",
    borderRadius: 6,
    overflow: "hidden",
  },
  barFill: { height: "100%", borderRadius: 6, transition: "width 0.4s ease" },
  rowCount: {
    fontFamily: "var(--font-mono)",
    fontSize: 13,
    color: "var(--text-secondary)",
    textAlign: "right",
  },
};
