/** Auto-refresh interval for dashboard data (ms). Set NEXT_PUBLIC_POLL_INTERVAL_MS at build time; clamped 10s–5min. */
const raw = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL_MS);
const parsed = Number.isFinite(raw) && raw > 0 ? raw : 30_000;

export const DASHBOARD_POLL_INTERVAL_MS = Math.min(300_000, Math.max(10_000, parsed));
