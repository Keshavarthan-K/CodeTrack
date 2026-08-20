import { useMemo, useState } from "react";

const DAY_MS = 24 * 60 * 60 * 1000;

function toDateKey(d) {
  return d.toISOString().slice(0, 10);
}

/**
 * GitHub-style calendar heatmap, restyled as a terminal "commit graph"
 * to match the rest of the dashboard - cells glow teal instead of
 * green, and today's cell has a blinking cursor outline.
 */
export default function ActivityHeatmap({ data, weeks = 26 }) {
  const [hover, setHover] = useState(null);

  const countByDate = useMemo(() => {
    const map = new Map();
    for (const row of data) map.set(row.date, row.count);
    return map;
  }, [data]);

  const maxCount = useMemo(
    () => Math.max(1, ...data.map((d) => d.count)),
    [data]
  );

  const columns = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    // Align the grid to end on the most recent Saturday, GitHub-style.
    const end = new Date(today);
    end.setDate(end.getDate() + (6 - end.getDay()));

    const cols = [];
    for (let w = weeks - 1; w >= 0; w--) {
      const col = [];
      for (let d = 0; d < 7; d++) {
        const date = new Date(end);
        date.setDate(date.getDate() - w * 7 - (6 - d));
        col.push(date);
      }
      cols.push(col);
    }
    return cols;
  }, [weeks]);

  const todayKey = toDateKey(new Date());

  const intensity = (count) => {
    if (!count) return 0;
    const ratio = count / maxCount;
    if (ratio > 0.75) return 4;
    if (ratio > 0.5) return 3;
    if (ratio > 0.25) return 2;
    return 1;
  };

  return (
    <div style={styles.wrap}>
      <div style={styles.promptRow}>
        <span style={styles.promptSymbol}>$</span>
        <span style={styles.promptText}>git log --graph --author=you --since="{weeks}w"</span>
      </div>

      <div style={styles.gridScroll}>
        <div style={styles.grid}>
          {columns.map((col, ci) => (
            <div key={ci} style={styles.col}>
              {col.map((date, di) => {
                const key = toDateKey(date);
                const count = countByDate.get(key) || 0;
                const level = intensity(count);
                const isToday = key === todayKey;
                const isFuture = date > new Date();
                return (
                  <div
                    key={di}
                    onMouseEnter={() => setHover({ key, count })}
                    onMouseLeave={() => setHover(null)}
                    style={{
                      ...styles.cell,
                      background: isFuture
                        ? "transparent"
                        : cellColor(level),
                      border: isToday
                        ? "1.5px solid var(--accent)"
                        : "1px solid var(--border-soft)",
                      boxShadow: isToday ? "0 0 0 2px rgba(94,234,212,0.15)" : "none",
                      cursor: isFuture ? "default" : "pointer",
                    }}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <div style={styles.footerRow}>
        <span style={styles.hoverLabel}>
          {hover
            ? `${hover.key} — ${hover.count} solve${hover.count === 1 ? "" : "s"}`
            : "hover a cell to inspect a commit"}
        </span>
        <div style={styles.legend}>
          <span style={styles.legendLabel}>less</span>
          {[0, 1, 2, 3, 4].map((l) => (
            <div key={l} style={{ ...styles.legendCell, background: cellColor(l) }} />
          ))}
          <span style={styles.legendLabel}>more</span>
        </div>
      </div>
    </div>
  );
}

function cellColor(level) {
  return [
    "#171d2b",
    "rgba(94, 234, 212, 0.25)",
    "rgba(94, 234, 212, 0.45)",
    "rgba(94, 234, 212, 0.7)",
    "#5eead4",
  ][level];
}

const styles = {
  wrap: {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-lg)",
    padding: "20px 20px 16px",
  },
  promptRow: {
    display: "flex",
    gap: 8,
    alignItems: "baseline",
    marginBottom: 16,
    fontFamily: "var(--font-mono)",
    fontSize: 13,
  },
  promptSymbol: { color: "var(--accent)" },
  promptText: { color: "var(--text-secondary)" },
  gridScroll: { overflowX: "auto", paddingBottom: 4 },
  grid: { display: "flex", gap: 3, width: "fit-content" },
  col: { display: "flex", flexDirection: "column", gap: 3 },
  cell: { width: 11, height: 11, borderRadius: 2 },
  footerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 14,
    fontFamily: "var(--font-mono)",
    fontSize: 11,
    color: "var(--text-faint)",
  },
  hoverLabel: { color: "var(--text-secondary)" },
  legend: { display: "flex", alignItems: "center", gap: 4 },
  legendLabel: { color: "var(--text-faint)", marginRight: 2, fontSize: 11 },
  legendCell: { width: 10, height: 10, borderRadius: 2 },
};
