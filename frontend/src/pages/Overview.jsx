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
          <strong>{statistics.total_matches.toLocaleString()}</strong>
          <small>Historical matches analyzed</small>
        </div>

        <div className="stat-card">
          <span>Home Wins</span>
          <strong>{statistics.home_win_percentage}%</strong>
          <small>{statistics.home_wins.toLocaleString()} matches</small>
        </div>

        <div className="stat-card">
          <span>Draws</span>
          <strong>{statistics.draw_percentage}%</strong>
          <small>{statistics.draws.toLocaleString()} matches</small>
        </div>

        <div className="stat-card">
          <span>Away Wins</span>
          <strong>{statistics.away_win_percentage}%</strong>
          <small>{statistics.away_wins.toLocaleString()} matches</small>
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

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={outcomeData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={115}
                  paddingAngle={3}
                >
                  {outcomeData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        ["#541E5D", "#9B6AA3", "#D8CFDA"][index]
                      }
                    />
                  ))}
                </Pie>

                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="outcome-legend">
            <div>
              <span className="legend-dot home"></span>
              <span>Home Wins</span>
              <strong>{statistics.home_win_percentage}%</strong>
            </div>

            <div>
              <span className="legend-dot draw"></span>
              <span>Draws</span>
              <strong>{statistics.draw_percentage}%</strong>
            </div>

            <div>
              <span className="legend-dot away"></span>
              <span>Away Wins</span>
              <strong>{statistics.away_win_percentage}%</strong>
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