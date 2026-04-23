import React, { useState, useEffect, useCallback, useRef } from "react";
import { useNavigation } from '../components/infrastructure/NavigationProvider.js';
import { ViewKeys } from './viewKeys.js';
import './AnalyticsView.css'; 

interface TopAirline {
  airline: string;
  origin_country: string;
  flight_count: number;
  avg_altitude: number;
  avg_velocity: number;
  max_altitude: number;
}

interface PeakHour {
  hour: string;
  origin_country: string;
  flight_count: number;
  avg_altitude: number;
}

interface AltitudeByAirline {
  airline: string;
  total_flights: number;
  avg_altitude: number;
  altitude_stddev: number;
  min_altitude: number;
  max_altitude: number;
}

interface CountryStat {
  origin_country: string;
  total_flights: number;
  unique_aircraft: number;
  avg_altitude: number;
  avg_velocity: number;
}

interface RegionStat {
  region: string;
  flight_count: number;
  avg_altitude: number;
  avg_velocity: number;
}

interface AnalyticsData {
  topAirlines: TopAirline[];
  peakHours: PeakHour[];
  altitudeByAirline: AltitudeByAirline[];
  countries: CountryStat[];
  regions: RegionStat[];
}

const BASE = "http://localhost:8000";

async function fetchAll(): Promise<AnalyticsData> {
  const [a, b, c, d, e] = await Promise.all([
    fetch(`${BASE}/api/analytics/top-airlines?limit=10`).then((r) => r.json()),
    fetch(`${BASE}/api/analytics/peak-hours`).then((r) => r.json()),
    fetch(`${BASE}/api/analytics/altitude-by-airline?limit=15`).then((r) =>
      r.json(),
    ),
    fetch(`${BASE}/api/analytics/countries?limit=20`).then((r) => r.json()),
    fetch(`${BASE}/api/analytics/regions`).then((r) => r.json()),
  ]);
  return {
    topAirlines: a.airlines ?? [],
    peakHours: b.peak_hours ?? [],
    altitudeByAirline: c.airlines ?? [],
    countries: d.countries ?? [],
    regions: e.regions ?? [],
  };
}
const fmt = (n: number) => n.toLocaleString("en-US");
const fmtM = (m: number) => `${Math.round(m)} m`;
const fmtKmh = (v: number) => `${Math.round(v)} km/h`;

function maxOf<T>(arr: T[], key: keyof T): number {
  return Math.max(...arr.map((x) => Number(x[key])));
}

function Bar({
  pct,
  color = "var(--accent)",
  height = 6,
}: {
  pct: number;
  color?: string;
  height?: number;
}) {
  return (
    <div
      style={{
        height,
        borderRadius: 4,
        background: "var(--bar-bg)",
        overflow: "hidden",
        width: "100%",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${Math.min(100, pct)}%`,
          background: color,
          borderRadius: 4,
          transition: "width 0.8s cubic-bezier(0.4,0,0.2,1)",
        }}
      />
    </div>
  );
}

/** Metric pill */
function Pill({ label, value }: { label: string; value: string }) {
  return (
    <span style={{ display: "inline-flex", flexDirection: "column", gap: 1 }}>
      <span style={{ fontSize: 10, color: "var(--muted)", letterSpacing: 1 }}>
        {label}
      </span>
      <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>
        {value}
      </span>
    </span>
  );
}

function Card({
  title,
  icon,
  children,
  style,
}: {
  title: string;
  icon: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <div className="av-card" style={style}>
      <div className="av-card-header">
        <span className="av-card-icon">{icon}</span>
        <span className="av-card-title">{title}</span>
      </div>
      {children}
    </div>
  );
}

function TopAirlinesSection({ data }: { data: TopAirline[] }) {
  const maxFlights = maxOf(data, "flight_count");
  return (
    <Card title="Top Airlines" icon="✈">
      <div className="av-list">
        {data.map((a, i) => (
          <div key={a.airline} className="av-list-row">
            <div className="av-list-rank">{i + 1}</div>
            <div className="av-list-main">
              <div className="av-list-name-row">
                <span className="av-airline-code">{a.airline}</span>
                <span className="av-country-badge">{a.origin_country}</span>
                <span className="av-count">{fmt(a.flight_count)} flights</span>
              </div>
              <Bar pct={(a.flight_count / maxFlights) * 100} />
              <div className="av-pills">
                <Pill label="Avg altitude" value={fmtM(a.avg_altitude)} />
                <Pill label="Avg speed" value={fmtKmh(a.avg_velocity)} />
                <Pill label="Max altitude" value={fmtM(a.max_altitude)} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function PeakHoursSection({ data }: { data: PeakHour[] }) {
  const byHour = Array.from({ length: 24 }, (_, h) => {
    const rows = data.filter((d) => Number(d.hour) === h);
    const count = rows.reduce((s, r) => s + r.flight_count, 0);
    return { hour: h, count };
  });
  const maxCount = Math.max(...byHour.map((h) => h.count), 1);

  return (
    <Card title="Peak Hours" icon="🕐">
      <div className="av-heatmap">
        {byHour.map(({ hour, count }) => {
          const intensity = count / maxCount;
          return (
            <div
              key={hour}
              className="av-hour-cell"
              style={
                {
                  "--intensity": intensity,
                  background:
                    count > 0
                      ? `rgba(var(--accent-rgb), ${0.12 + intensity * 0.75})`
                      : "var(--bar-bg)",
                } as React.CSSProperties
              }
              title={`${hour}:00 — ${fmt(count)} flights`}
            >
              <span className="av-hour-label">{hour}</span>
              {count > 0 && <span className="av-hour-count">{fmt(count)}</span>}
            </div>
          );
        })}
      </div>
      <div className="av-heatmap-legend">
        <span>0:00</span>
        <span style={{ color: "var(--muted)", fontSize: 11 }}>
          Flight intensity by hour
        </span>
        <span>23:00</span>
      </div>
    </Card>
  );
}

function AltitudeSection({ data }: { data: AltitudeByAirline[] }) {
  const sorted = [...data].sort((a, b) => b.avg_altitude - a.avg_altitude);
  const maxAlt = maxOf(sorted, "max_altitude");

  return (
    <Card title="Altitude by Airline" icon="📡">
      <div className="av-alt-list">
        {sorted.map((a) => {
          const minPct = (a.min_altitude / maxAlt) * 100;
          const maxPct = (a.max_altitude / maxAlt) * 100;
          const avgPct = (a.avg_altitude / maxAlt) * 100;

          return (
            <div key={a.airline} className="av-alt-row">
              <div className="av-alt-label">
                <span className="av-airline-code">{a.airline}</span>
                <span style={{ color: "var(--muted)", fontSize: 11 }}>
                  {fmt(a.total_flights)} flights
                </span>
              </div>
              {/* Range bar */}
              <div className="av-alt-track">
                <div
                  className="av-alt-range"
                  style={{ left: `${minPct}%`, width: `${maxPct - minPct}%` }}
                />
                <div
                  className="av-alt-avg"
                  style={{ left: `${avgPct}%` }}
                  title={`Avg: ${fmtM(a.avg_altitude)}`}
                />
              </div>
              <span className="av-alt-avg-label">{fmtM(a.avg_altitude)}</span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

// ─── Section: Countries ────────────────────────────────────────────────────

function CountriesSection({ data }: { data: CountryStat[] }) {
  const sorted = [...data].sort((a, b) => b.total_flights - a.total_flights);
  const maxFlights = maxOf(sorted, "total_flights");

  return (
    <Card title="By Country" icon="🌍">
      <div className="av-country-table">
        <div className="av-country-header">
          <span>Country</span>
          <span>Flights</span>
          <span>A/C</span>
          <span>Altitude</span>
          <span>Speed</span>
        </div>
        {sorted.map((c) => (
          <div key={c.origin_country} className="av-country-row">
            <div className="av-country-name-col">
              <span>{c.origin_country}</span>
              <Bar
                pct={(c.total_flights / maxFlights) * 100}
                color="var(--accent2)"
                height={3}
              />
            </div>
            <span>{fmt(c.total_flights)}</span>
            <span>{fmt(c.unique_aircraft)}</span>
            <span>{fmtM(c.avg_altitude)}</span>
            <span>{fmtKmh(c.avg_velocity)}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

function RegionsSection({ data }: { data: RegionStat[] }) {
  const sorted = [...data].sort((a, b) => b.flight_count - a.flight_count);
  const total = sorted.reduce((s, r) => s + r.flight_count, 0) || 1;

  const COLORS = [
    "var(--accent)",
    "var(--accent2)",
    "var(--accent3)",
    "#f59e0b",
    "#10b981",
    "#8b5cf6",
    "#ec4899",
    "#06b6d4",
  ];

  return (
    <Card title="By Region" icon="🗺">
      <div className="av-regions">
        {sorted.map((r, i) => {
          const pct = (r.flight_count / total) * 100;
          return (
            <div key={r.region} className="av-region-row">
              <div
                className="av-region-dot"
                style={{ background: COLORS[i % COLORS.length] }}
              />
              <div className="av-region-main">
                <div className="av-region-name-row">
                  <span className="av-region-name">{r.region}</span>
                  <span className="av-region-pct">{pct.toFixed(1)}%</span>
                  <span className="av-region-count">
                    {fmt(r.flight_count)} flights
                  </span>
                </div>
                <Bar pct={pct} color={COLORS[i % COLORS.length]} height={5} />
                <div className="av-pills">
                  <Pill label="Avg altitude" value={fmtM(r.avg_altitude)} />
                  <Pill label="Avg speed" value={fmtKmh(r.avg_velocity)} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

const REFRESH_INTERVAL = 60_000;

export default function AnalyticsView() {
  const { navigateByKey } = useNavigation();
  const [isOpen, setIsOpen] = useState(true);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [countdown, setCountdown] = useState(REFRESH_INTERVAL / 1000);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setCountdown(REFRESH_INTERVAL / 1000);
    try {
      const result = await fetchAll();
      setData(result);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error loading data");
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh
  useEffect(() => {
    load();
    timerRef.current = setInterval(load, REFRESH_INTERVAL);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [load]);

  // Countdown ticker
  useEffect(() => {
    countdownRef.current = setInterval(() => {
      setCountdown((c) => (c <= 1 ? REFRESH_INTERVAL / 1000 : c - 1));
    }, 1000);
    return () => {
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []);

  const handleRefresh = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    load();
    timerRef.current = setInterval(load, REFRESH_INTERVAL);
  };

  const handleClose = () => {
    navigateByKey(ViewKeys.MapView);
  };

  if (!isOpen) return null;
  return (
    <>
      <div className="av-root">
        {/* Header */}
        <header className="av-header">
          <div className="av-header-left">
            <div className="av-logo-title">Analytics</div>
          </div>

          <div className="av-header-right">
            {lastUpdated && (
              <span className="av-updated">
                Updated: {lastUpdated.toLocaleTimeString("en-US")} 
                {/* · next in {countdown}s */}
              </span>
            )}
    
            <button
              className="av-refresh-btn"
              onClick={handleRefresh}
              disabled={loading}
              title="Refresh data"
            >
              <span
                className="av-refresh-icon"
                style={{
                  animation: loading ? "av-spin 1s linear infinite" : "none",
                }}
              >
                ↻
              </span>
              Refresh
            </button>
         <button
              className="av-close-btn"
              onClick={handleClose}
              title="Close analytics"
            >
              ✕
            </button>
          </div>
        </header>

        {/* Body */}
        <main className="av-main">
          {/* Loading */}
          {loading && !data && (
            <div className="av-center">
              <div className="av-spinner" />
              <div className="av-loading-text">Loading data…</div>
            </div>
          )}

          {/* Error */}
          {error && !data && (
            <div className="av-center">
              <div className="av-error-card">
                <div className="av-error-icon">⚠</div>
                <div className="av-error-title">Loading Error</div>
                <div className="av-error-msg">{error}</div>
                <button className="av-retry-btn" onClick={handleRefresh}>
                  Retry
                </button>
              </div>
            </div>
          )}

          {/* Data */}
          {data && (
            <div className="av-grid">
              <TopAirlinesSection data={data.topAirlines} />
              <CountriesSection data={data.countries} />
            </div>
          )}
        </main>
      </div>
    </>
  );
}