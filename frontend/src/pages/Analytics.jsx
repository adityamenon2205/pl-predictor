import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import { getTeamStatistics } from "../services/api";
import teamMetadata from "../data/teams";


function Analytics() {
  const [searchParams] = useSearchParams();

  const selectedTeam = searchParams.get("team");

  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const theme = teamMetadata[selectedTeam] || {
    primary: "#541E5D",
    secondary: "#FFFFFF",
    accent: "#541E5D",
  };


  useEffect(() => {
    if (!selectedTeam) {
      setStats(null);
      setLoading(false);
      return;
    }

    async function loadStatistics() {
      try {
        setLoading(true);
        setError(null);

        const data = await getTeamStatistics(selectedTeam);

        setStats(data);
      } catch (err) {
        setError("Unable to load team statistics.");
      } finally {
        setLoading(false);
      }
    }

    loadStatistics();
  }, [selectedTeam]);


  if (!selectedTeam) {
    return (
      <div className="analytics-page">
        <div className="page-header">
          <div>
            <p className="eyebrow">LEAGUE ANALYTICS</p>

            <h1>Analytics</h1>

            <p className="page-description">
              Select a team from the Teams page to explore
              historical performance.
            </p>
          </div>
        </div>
      </div>
    );
  }


  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-loading">
          Loading {selectedTeam} statistics...
        </div>
      </div>
    );
  }


  if (error) {
    return (
      <div className="analytics-page">
        <div className="analytics-error">
          {error}
        </div>
      </div>
    );
  }


  const resultData = [
    {
      name: "Wins",
      value: stats.wins,
    },
    {
      name: "Draws",
      value: stats.draws,
    },
    {
      name: "Losses",
      value: stats.losses,
    },
  ];


  const goalData = [
    {
      name: "Goals",
      Scored: stats.goals_scored,
      Conceded: stats.goals_conceded,
    },
  ];


  const venueData = [
    {
      name: "Home",
      Wins: stats.home.wins,
      Draws: stats.home.draws,
      Losses: stats.home.losses,
    },
    {
      name: "Away",
      Wins: stats.away.wins,
      Draws: stats.away.draws,
      Losses: stats.away.losses,
    },
  ];


  return (
    <div
      className="analytics-page"
      style={{
        "--team-primary": theme.primary,
        "--team-secondary": theme.secondary,
        "--team-accent": theme.accent,
      }}
    >

      {/* -------------------------------- */}
      {/* HEADER */}
      {/* -------------------------------- */}

      <div className="analytics-header">

        <div className="analytics-team-identity">

          <div className="analytics-team-crest">
            {theme.crest && (
              <img
                src={theme.crest}
                alt={`${selectedTeam} crest`}
              />
            )}
          </div>

          <div>
            <p className="eyebrow">TEAM ANALYTICS</p>

            <h1>{selectedTeam}</h1>

            <p className="page-description">
              Historical performance analysis for {selectedTeam}.
            </p>
          </div>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* KPI CARDS */}
      {/* -------------------------------- */}

      <div className="analytics-kpi-grid">

        <div className="analytics-kpi-card">
          <span>Matches</span>
          <strong>{stats.matches_played}</strong>
          <small>Historical matches</small>
        </div>

        <div className="analytics-kpi-card">
          <span>Wins</span>
          <strong>{stats.wins}</strong>
          <small>{stats.win_percentage}% win rate</small>
        </div>

        <div className="analytics-kpi-card">
          <span>Draws</span>
          <strong>{stats.draws}</strong>
          <small>{stats.draw_percentage}% draw rate</small>
        </div>

        <div className="analytics-kpi-card">
          <span>Losses</span>
          <strong>{stats.losses}</strong>
          <small>{stats.loss_percentage}% loss rate</small>
        </div>

      </div>


      {/* -------------------------------- */}
      {/* CHART ROW */}
      {/* -------------------------------- */}

      <div className="analytics-chart-grid">

        {/* RESULT DISTRIBUTION */}

        <div className="analytics-panel">

          <div className="analytics-panel-header">
            <div>
              <h2>Match Results</h2>
              <p>Overall historical record</p>
            </div>
          </div>

          <div className="result-chart">

            <ResponsiveContainer width="100%" height={280}>
              <PieChart>

                <Pie
                  data={resultData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={72}
                  outerRadius={105}
                  paddingAngle={3}
                >

                  <Cell fill={theme.primary} />
                  <Cell fill={theme.secondary} />
                  <Cell fill="#777777" />

                </Pie>

                <Tooltip
                  contentStyle={{
                    background: "#211122",
                    border: "1px solid rgba(255,255,255,0.15)",
                    borderRadius: "10px",
                    color: "#ffffff",
                  }}
                />

              </PieChart>
            </ResponsiveContainer>

            <div className="result-legend">

              <div>
                <span
                  style={{
                    background: theme.primary,
                  }}
                />
                <label>Wins</label>
                <strong>{stats.wins}</strong>
              </div>

              <div>
                <span
                  style={{
                    background: theme.secondary,
                  }}
                />
                <label>Draws</label>
                <strong>{stats.draws}</strong>
              </div>

              <div>
                <span
                  style={{
                    background: "#777777",
                  }}
                />
                <label>Losses</label>
                <strong>{stats.losses}</strong>
              </div>

            </div>

          </div>

        </div>


        {/* GOALS */}

        <div className="analytics-panel">

          <div className="analytics-panel-header">
            <div>
              <h2>Goals</h2>
              <p>Scored versus conceded</p>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart
              data={goalData}
              margin={{
                top: 30,
                right: 20,
                left: 0,
                bottom: 10,
              }}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.08)"
              />

              <XAxis
                dataKey="name"
                stroke="rgba(255,255,255,0.55)"
              />

              <YAxis
                stroke="rgba(255,255,255,0.55)"
              />

              <Tooltip
                contentStyle={{
                  background: "#211122",
                  border: "1px solid rgba(255,255,255,0.15)",
                  borderRadius: "10px",
                  color: "#ffffff",
                }}
              />

              <Bar
                dataKey="Scored"
                fill={theme.primary}
                radius={[6, 6, 0, 0]}
              />

              <Bar
                dataKey="Conceded"
                fill={theme.secondary}
                radius={[6, 6, 0, 0]}
              />

            </BarChart>
          </ResponsiveContainer>

          <div className="goal-summary">

            <div>
              <span>Scored</span>
              <strong>{stats.goals_scored}</strong>
            </div>

            <div>
              <span>Conceded</span>
              <strong>{stats.goals_conceded}</strong>
            </div>

            <div>
              <span>Difference</span>
              <strong>
                {stats.goal_difference > 0 ? "+" : ""}
                {stats.goal_difference}
              </strong>
            </div>

          </div>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* HOME VS AWAY */}
      {/* -------------------------------- */}

      <div className="analytics-panel venue-panel">

        <div className="analytics-panel-header">

          <div>
            <h2>Home vs Away Performance</h2>
            <p>Historical record by venue</p>
          </div>

        </div>


        <ResponsiveContainer width="100%" height={300}>

          <BarChart
            data={venueData}
            margin={{
              top: 20,
              right: 20,
              left: 0,
              bottom: 10,
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.08)"
            />

            <XAxis
              dataKey="name"
              stroke="rgba(255,255,255,0.55)"
            />

            <YAxis
              stroke="rgba(255,255,255,0.55)"
            />

            <Tooltip
              contentStyle={{
                background: "#211122",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: "10px",
                color: "#ffffff",
              }}
            />

            <Bar
              dataKey="Wins"
              fill={theme.primary}
              radius={[5, 5, 0, 0]}
            />

            <Bar
              dataKey="Draws"
              fill={theme.secondary}
              radius={[5, 5, 0, 0]}
            />

            <Bar
              dataKey="Losses"
              fill="#777777"
              radius={[5, 5, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>


        <div className="venue-summary">

          <div>
            <h3>Home</h3>
            <p>
              {stats.home.wins}W · {stats.home.draws}D ·{" "}
              {stats.home.losses}L
            </p>
            <span>
              {stats.home.matches} matches
            </span>
          </div>

          <div>
            <h3>Away</h3>
            <p>
              {stats.away.wins}W · {stats.away.draws}D ·{" "}
              {stats.away.losses}L
            </p>
            <span>
              {stats.away.matches} matches
            </span>
          </div>

        </div>

      </div>


      {/* -------------------------------- */}
      {/* GOAL DIFFERENCE */}
      {/* -------------------------------- */}

      <div className="analytics-highlight">

        <div>

          <span>GOAL DIFFERENCE</span>

          <strong>
            {stats.goal_difference > 0 ? "+" : ""}
            {stats.goal_difference}
          </strong>

        </div>

        <p>
          {selectedTeam} has scored{" "}
          <strong>{stats.goals_scored}</strong>{" "}
          goals while conceding{" "}
          <strong>{stats.goals_conceded}</strong>{" "}
          across {stats.matches_played} historical matches.
        </p>

      </div>

    </div>
  );
}

export default Analytics;