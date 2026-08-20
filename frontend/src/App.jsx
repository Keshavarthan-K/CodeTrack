import { useEffect, useState } from "react";
import { api } from "./api";
import StatCards from "./components/StatCards";
import ActivityHeatmap from "./components/ActivityHeatmap";
import PlatformBars from "./components/PlatformBars";
import MonthlyChart from "./components/MonthlyChart";
import DifficultyBars from "./components/DifficultyBars";

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [heatmap, setHeatmap] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [difficulty, setDifficulty] = useState({});
  const [error, setError] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);

  const loadAll = () => {
    setError(null);
    Promise.all([
      api.dashboard(),
      api.heatmap(),
      api.monthly(),
      api.difficulty(),
    ])
      .then(([d, h, m, diff]) => {
        setDashboard(d);
        setHeatmap(h);
        setMonthly(m);
        setDifficulty(diff);
      })
      .catch((e) => setError(e.message));
  };

  useEffect(loadAll, []);

  const handleSync = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const result = await api.syncCodeforces();
      setSyncMessage(
        `synced — ${result.new_solves} new solve${result.new_solves === 1 ? "" : "s"}, ` +
          `${result.new_problems} new problem${result.new_problems === 1 ? "" : "s"}`
      );
      loadAll();
    } catch (e) {
      setSyncMessage(`sync failed: ${e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  if (error) {
    return (
      <div style={styles.page}>
        <div style={styles.errorBox}>
          <div style={styles.errorTitle}>connection failed</div>
          <div style={styles.errorText}>
            Couldn't reach the CodeTrack API at the configured URL. Make sure the backend is
            running (<code>uvicorn app.main:app --reload</code>) and{" "}
            <code>VITE_API_URL</code> points at it.
          </div>
          <div style={styles.errorDetail}>{error}</div>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div style={styles.page}>
        <div style={styles.loading}>
          <span style={styles.cursor}>█</span> loading dashboard…
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <div>
          <div style={styles.promptLine}>
            <span style={styles.promptUser}>you</span>
            <span style={styles.promptAt}>@</span>
            <span style={styles.promptHost}>codetrack</span>
            <span style={styles.promptColon}>:~$</span>
            <span style={styles.promptCmd}> ./dashboard</span>
          </div>
          <h1 style={styles.h1}>CodeTrack</h1>
          <div style={styles.subtitle}>coding progress analytics</div>
        </div>

        <button style={styles.syncButton} onClick={handleSync} disabled={syncing}>
          {syncing ? "syncing…" : "↻ sync codeforces"}
        </button>
      </header>

      {syncMessage && <div style={styles.syncMessage}>{syncMessage}</div>}

      <StatCards dashboard={dashboard} />

      <ActivityHeatmap data={heatmap} />

      <div className="two-col">
        <PlatformBars platforms={dashboard.platforms} />
        <DifficultyBars difficulty={difficulty} />
      </div>

      <MonthlyChart data={monthly} />

      <footer style={styles.footer}>
        every number above is derived from first_solved_at — resubmitting a solved problem never
        moves the needle.
      </footer>
    </div>
  );
}

const styles = {
  page: {
    maxWidth: 920,
    margin: "0 auto",
    padding: "48px 24px 80px",
    display: "flex",
    flexDirection: "column",
    gap: 20,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-end",
    marginBottom: 8,
    flexWrap: "wrap",
    gap: 16,
  },
  promptLine: {
    fontFamily: "var(--font-mono)",
    fontSize: 13,
    marginBottom: 10,
  },
  promptUser: { color: "var(--accent)" },
  promptAt: { color: "var(--text-faint)" },
  promptHost: { color: "var(--accent-warm)" },
  promptColon: { color: "var(--text-faint)" },
  promptCmd: { color: "var(--text-secondary)" },
  h1: {
    fontFamily: "var(--font-display)",
    fontSize: 40,
    fontWeight: 700,
    margin: 0,
    letterSpacing: -0.5,
  },
  subtitle: {
    color: "var(--text-secondary)",
    fontSize: 14,
    marginTop: 4,
  },
  syncButton: {
    fontFamily: "var(--font-mono)",
    fontSize: 13,
    background: "var(--surface-raised)",
    border: "1px solid var(--border)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-md)",
    padding: "10px 16px",
    cursor: "pointer",
  },
  syncMessage: {
    fontFamily: "var(--font-mono)",
    fontSize: 12,
    color: "var(--accent)",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-sm)",
    padding: "10px 14px",
  },
  footer: {
    marginTop: 20,
    fontFamily: "var(--font-mono)",
    fontSize: 11,
    color: "var(--text-faint)",
    textAlign: "center",
    lineHeight: 1.6,
  },
  loading: {
    fontFamily: "var(--font-mono)",
    fontSize: 14,
    color: "var(--text-secondary)",
    marginTop: 100,
    textAlign: "center",
  },
  cursor: { color: "var(--accent)" },
  errorBox: {
    marginTop: 100,
    background: "var(--surface)",
    border: "1px solid var(--accent-danger)",
    borderRadius: "var(--radius-lg)",
    padding: 24,
  },
  errorTitle: {
    fontFamily: "var(--font-mono)",
    color: "var(--accent-danger)",
    fontSize: 14,
    marginBottom: 8,
  },
  errorText: {
    color: "var(--text-secondary)",
    fontSize: 14,
    lineHeight: 1.6,
  },
  errorDetail: {
    marginTop: 12,
    fontFamily: "var(--font-mono)",
    fontSize: 12,
    color: "var(--text-faint)",
  },
};
