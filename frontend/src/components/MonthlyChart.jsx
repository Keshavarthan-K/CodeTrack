import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={styles.tooltip}>
      <div style={styles.tooltipLabel}>{label}</div>
      <div style={styles.tooltipValue}>{payload[0].value} solved</div>
    </div>
  );
}

export default function MonthlyChart({ data }) {
  // Keep the last 12 months so the chart stays legible.
  const recent = data.slice(-12);

  return (
    <div style={styles.wrap}>
      <div style={styles.title}>monthly progress (last 12 months)</div>
      <div style={{ width: "100%", height: 200 }}>
        <ResponsiveContainer>
          <BarChart data={recent} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <XAxis
              dataKey="month"
              tick={{ fill: "var(--text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={{ stroke: "var(--border)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "var(--text-faint)", fontSize: 11, fontFamily: "var(--font-mono)" }}
              axisLine={false}
              tickLine={false}
              width={30}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(94,234,212,0.06)" }} />
            <Bar dataKey="count" fill="var(--accent)" radius={[3, 3, 0, 0]} maxBarSize={28} />
          </BarChart>
        </ResponsiveContainer>
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
    marginBottom: 12,
  },
  tooltip: {
    background: "var(--surface-raised)",
    border: "1px solid var(--border)",
    borderRadius: 6,
    padding: "8px 12px",
    fontFamily: "var(--font-mono)",
  },
  tooltipLabel: { fontSize: 11, color: "var(--text-secondary)" },
  tooltipValue: { fontSize: 13, color: "var(--accent)", marginTop: 2 },
};
