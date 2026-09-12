import { useEffect, useState } from "react";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { getStatistics, getTeams } from "../services/api";

function Overview() {
  const [statistics, setStatistics] = useState(null);
  const [teamCount, setTeamCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [statsData, teamsData] = await Promise.all([
          getStatistics(),
          getTeams(),
        ]);

        setStatistics(statsData);
        setTeamCount(teamsData.teams.length);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="overview-page">
        <h1>Overview</h1>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="overview-page">
        <h1>Overview</h1>
        <p>Unable to load dashboard data.</p>
        <span>{error}</span>
      </div>
    );
  }

  const outcomeData = [
    {
      name: "Home Wins",
      value: statistics.home_wins,
    },
    {
      name: "Draws",
      value: statistics.draws,
    },
    {
      name: "Away Wins",
      value: statistics.away_wins,
    },
  ];

  return (
    <div className="overview-page">
      <div className="page-header">
        <div>
          <p className="eyebrow">PREMIER LEAGUE ANALYTICS</p>
          <h1>Overview</h1>
          <p className="page-description">
            A statistical overview of Premier League match data.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total Matches</span>
          <strong>
            {statistics.total_matches.toLocaleString()}
          </strong>
          <small>Historical matches analyzed</small>
        </div>

        <div className="stat-card">
          <span>Home Wins</span>
          <strong>{statistics.home_win_percentage}%</strong>
          <small>
            {statistics.home_wins.toLocaleString()} matches
          </small>
        </div>

        <div className="stat-card">
          <span>Draws</span>
          <strong>{statistics.draw_percentage}%</strong>
          <small>
            {statistics.draws.toLocaleString()} matches
          </small>
        </div>

        <div className="stat-card">
          <span>Away Wins</span>
          <strong>{statistics.away_win_percentage}%</strong>
          <small>
            {statistics.away_wins.toLocaleString()} matches
          </small>
        </div>
      </div>

      <div className="overview-grid">
        <section className="dashboard-card outcome-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">MATCH RESULTS</p>
              <h2>Outcome Distribution</h2>
            </div>
          </div>

          <div className="chart-container outcome-chart-container">
            <ResponsiveContainer width="100%" height={340}>
              <PieChart>
                <defs>
                  {/* Home Wins - Coral */}
                  <linearGradient
                    id="homeGradient"
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#F26B5B"
                    />
                    <stop
                      offset="100%"
                      stopColor="#E95545"
                    />
                  </linearGradient>

                  {/* Draws - Golden Yellow */}
                  <linearGradient
                    id="drawGradient"
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#FFD166"
                    />
                    <stop
                      offset="100%"
                      stopColor="#F5B942"
                    />
                  </linearGradient>

                  {/* Away Wins - Teal */}
                  <linearGradient
                    id="awayGradient"
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#4FC3B1"
                    />
                    <stop
                      offset="100%"
                      stopColor="#35A895"
                    />
                  </linearGradient>

                  {/* Subtle glow around the chart */}
                  <filter
                    id="donutGlow"
                    x="-50%"
                    y="-50%"
                    width="200%"
                    height="200%"
                  >
                    <feGaussianBlur
                      stdDeviation="7"
                      result="blur"
                    />

                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>

                <Pie
                  data={outcomeData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={95}
                  outerRadius={140}
                  paddingAngle={3}
                  stroke="#F7F3F8"
                  strokeWidth={2}
                  // filter="url(#donutGlow)"
                  isAnimationActive={true}
                  animationDuration={900}
                  animationEasing="ease-out"
                >
                  <Cell fill="url(#homeGradient)" />
                  <Cell fill="url(#drawGradient)" />
                  <Cell fill="url(#awayGradient)" />
                </Pie>

                <Tooltip
                  formatter={(value, name) => [
                    `${value.toLocaleString()} matches`,
                    name,
                  ]}
                  contentStyle={{
                    backgroundColor: "#241025",
                    border: "1px solid rgba(255, 255, 255, 0.12)",
                    borderRadius: "10px",
                    color: "#ffffff",
                    boxShadow: "0 10px 30px rgba(0, 0, 0, 0.3)",
                  }}
                  labelStyle={{
                    color: "#ffffff",
                    fontWeight: 600,
                  }}
                  itemStyle={{
                    color: "#ffffff",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="outcome-legend">
            <div>
              <span className="legend-dot home"></span>
              <span>Home Wins</span>
              <strong>
                {statistics.home_win_percentage}%
              </strong>
            </div>

            <div>
              <span className="legend-dot draw"></span>
              <span>Draws</span>
              <strong>
                {statistics.draw_percentage}%
              </strong>
            </div>

            <div>
              <span className="legend-dot away"></span>
              <span>Away Wins</span>
              <strong>
                {statistics.away_win_percentage}%
              </strong>
            </div>
          </div>
        </section>

        <section className="dashboard-card league-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">DATASET</p>
              <h2>League Snapshot</h2>
            </div>
          </div>

          <div className="snapshot-stat">
            <span>Teams</span>
            <strong>{teamCount}</strong>
          </div>

          <div className="snapshot-stat">
            <span>Matches analyzed</span>
            <strong>
              {statistics.total_matches.toLocaleString()}
            </strong>
          </div>

          <div className="snapshot-stat">
            <span>Most common result</span>
            <strong>
              {statistics.home_win_percentage >=
              Math.max(
                statistics.draw_percentage,
                statistics.away_win_percentage
              )
                ? "Home Win"
                : statistics.draw_percentage >=
                  statistics.away_win_percentage
                ? "Draw"
                : "Away Win"}
            </strong>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Overview;