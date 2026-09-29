import { cloneElement, useEffect, useRef, useState } from "react";
import { motion } from "motion/react";
import { useSearchParams } from "react-router-dom";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getLeagueAnalytics, getTeamStatistics } from "../services/api";

import teamMetadata from "../data/teams";
import PageTransition from "../components/common/PageTransition";
import AnimatedNumber from "../components/common/AnimatedNumber";

/*
 * =========================================
 * MEASURED RECHARTS CONTAINER
 * =========================================
 *
 * ResponsiveContainer was causing the league charts to
 * mount with their legend but without a usable SVG drawing
 * area in the current layout. This wrapper measures the
 * actual DOM width and passes a numeric width directly to
 * Recharts.
 */

function MeasuredChart({ children, height }) {
  const containerRef = useRef(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const element = containerRef.current;

    if (!element) {
      return undefined;
    }

    const updateWidth = () => {
      const nextWidth = Math.floor(element.getBoundingClientRect().width);

      if (nextWidth > 0) {
        setWidth(nextWidth);
      }
    };

    updateWidth();

    const observer = new ResizeObserver(updateWidth);
    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="analytics-chart"
      style={{
        width: "100%",
        height: `${height}px`,
      }}
    >
      {width > 0
        ? cloneElement(children, {
            width,
            height,
          })
        : null}
    </div>
  );
}

/*
 * =========================================
 * SEASON TREND DATA NORMALIZATION
 * =========================================
 *
 * Accepts the normal array response, but also safely handles
 * an object/dictionary response from the backend.
 */

function normalizeNumber(value) {
  const number = Number(value);

  return Number.isFinite(number) ? number : null;
}

function normalizeSeasonTrends(raw) {
  let rows = [];

  if (Array.isArray(raw)) {
    rows = raw;
  } else if (raw && Array.isArray(raw.data)) {
    rows = raw.data;
  } else if (raw && typeof raw === "object") {
    rows = Object.entries(raw).map(([season, values]) => ({
      season,
      ...(values || {}),
    }));
  }

  return rows
    .map((row) => ({
      season: row.season ?? row.Season ?? "",
      home_win_percentage: normalizeNumber(
        row.home_win_percentage ?? row.home_win_pct ?? row.home_win_rate,
      ),
      draw_percentage: normalizeNumber(
        row.draw_percentage ?? row.draw_pct ?? row.draw_rate,
      ),
      away_win_percentage: normalizeNumber(
        row.away_win_percentage ?? row.away_win_pct ?? row.away_win_rate,
      ),
      goals_per_match: normalizeNumber(
        row.goals_per_match ?? row.goalsPerMatch,
      ),
      home_goals_per_match: normalizeNumber(
        row.home_goals_per_match ?? row.home_goals_per_match_avg,
      ),
      away_goals_per_match: normalizeNumber(
        row.away_goals_per_match ?? row.away_goals_per_match_avg,
      ),
    }))
    .filter((row) => row.season !== "");
}

function Analytics() {
  const [searchParams] = useSearchParams();

  const selectedTeam = searchParams.get("team");

  /*
   * =========================================
   * TEAM ANALYTICS STATE
   * =========================================
   */

  const [teamStatistics, setTeamStatistics] = useState(null);

  /*
   * =========================================
   * LEAGUE ANALYTICS STATE
   * =========================================
   */

  const [leagueAnalytics, setLeagueAnalytics] = useState(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState(null);

  /*
   * =========================================
   * FETCH DATA
   * =========================================
   */

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        setError(null);

        /*
         * Team selected
         * → Load team analytics
         */

        if (selectedTeam) {
          const data = await getTeamStatistics(selectedTeam);

          setTeamStatistics(data);
          setLeagueAnalytics(null);

          return;
        }

        /*
         * No team selected
         * → Load league analytics
         */

        const data = await getLeagueAnalytics();

        setLeagueAnalytics(data);
        setTeamStatistics(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, [selectedTeam]);

  /*
   * =========================================
   * LOADING
   * =========================================
   */

  if (loading) {
    return (
      <PageTransition>
        <div className="analytics-page">
          <div className="analytics-loading">
            <p>Loading analytics...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  /*
   * =========================================
   * ERROR
   * =========================================
   */

  if (error) {
    return (
      <PageTransition>
        <div className="analytics-page">
          <div className="analytics-error">
            <h2>Unable to load analytics</h2>
            <p>{error}</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  /*
   * =========================================
   * TEAM ANALYTICS
   * =========================================
   */

  if (selectedTeam && teamStatistics) {
    const theme = teamMetadata[selectedTeam] || {
      primary: "#541E5D",
      secondary: "#FFFFFF",
      accent: "#541E5D",
      crest: null,
    };

    const resultData = [
      {
        name: "Wins",
        value: teamStatistics.wins,
      },
      {
        name: "Draws",
        value: teamStatistics.draws,
      },
      {
        name: "Losses",
        value: teamStatistics.losses,
      },
    ];

    const resultColors = [theme.primary, "#9B6AA3", "#D8CFDA"];

    const goalData = [
      {
        category: "Goals",
        scored: teamStatistics.goals_scored,
        conceded: teamStatistics.goals_conceded,
      },
    ];

    const venueData = [
      {
        category: "Home",
        wins: teamStatistics.home.wins,
        draws: teamStatistics.home.draws,
        losses: teamStatistics.home.losses,
      },
      {
        category: "Away",
        wins: teamStatistics.away.wins,
        draws: teamStatistics.away.draws,
        losses: teamStatistics.away.losses,
      },
    ];

    return (
      <PageTransition>
        <div className="analytics-page">
          {/* ================================
            TEAM HEADER
        ================================= */}

          <div
            className="analytics-header"
            style={{
              "--team-primary": theme.primary,
              "--team-secondary": theme.secondary,
              "--team-accent": theme.accent,
            }}
          >
            <div className="analytics-team-identity">
              <div className="analytics-team-crest">
                {theme.crest ? (
                  <img src={theme.crest} alt={`${selectedTeam} crest`} />
                ) : (
                  <div className="team-crest-fallback">
                    {selectedTeam.charAt(0)}
                  </div>
                )}
              </div>

              <div>
                <p className="eyebrow">TEAM ANALYTICS</p>

                <h1>{selectedTeam}</h1>

                <p className="page-description">
                  Historical Premier League performance across the available
                  dataset.
                </p>
              </div>
            </div>
          </div>

          {/* ================================
            KPI CARDS
        ================================= */}

          <motion.div
            className="analytics-kpi-grid"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.08 }}
          >
            <div className="analytics-kpi-card">
              <span>Matches</span>
              <strong>
                <AnimatedNumber
                  value={teamStatistics.matches_played}
                  duration={1.2}
                />
              </strong>
              <small>Historical matches</small>
            </div>

            <div className="analytics-kpi-card">
              <span>Wins</span>
              <strong>{teamStatistics.wins}</strong>
              <small>{teamStatistics.win_percentage}% win rate</small>
            </div>

            <div className="analytics-kpi-card">
              <span>Draws</span>
              <strong>{teamStatistics.draws}</strong>
              <small>{teamStatistics.draw_percentage}% draw rate</small>
            </div>

            <div className="analytics-kpi-card">
              <span>Losses</span>
              <strong>{teamStatistics.losses}</strong>
              <small>{teamStatistics.loss_percentage}% loss rate</small>
            </div>
          </motion.div>

          {/* ================================
            RESULT + GOALS
        ================================= */}

          <motion.div
            className="analytics-chart-grid"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.16 }}
          >
            <section className="analytics-panel">
              <div className="card-header">
                <div>
                  <p className="eyebrow">MATCH RESULTS</p>

                  <h2>Result Distribution</h2>
                </div>
              </div>

              <div className="result-chart">
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={resultData}
                      isAnimationActive={true}
                      animationDuration={800}
                      animationEasing="ease-out"
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={70}
                      outerRadius={105}
                      paddingAngle={3}
                    >
                      {resultData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={resultColors[index]}
                        />
                      ))}
                    </Pie>

                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="result-legend">
                <div>
                  <span
                    className="legend-dot"
                    style={{
                      backgroundColor: resultColors[0],
                    }}
                  />

                  <span>Wins</span>

                  <strong>{teamStatistics.win_percentage}%</strong>
                </div>

                <div>
                  <span
                    className="legend-dot"
                    style={{
                      backgroundColor: resultColors[1],
                    }}
                  />

                  <span>Draws</span>

                  <strong>{teamStatistics.draw_percentage}%</strong>
                </div>

                <div>
                  <span
                    className="legend-dot"
                    style={{
                      backgroundColor: resultColors[2],
                    }}
                  />

                  <span>Losses</span>

                  <strong>{teamStatistics.loss_percentage}%</strong>
                </div>
              </div>
            </section>

            {/* GOALS */}

            <section className="analytics-panel">
              <div className="card-header">
                <div>
                  <p className="eyebrow">GOAL RECORD</p>

                  <h2>Goals Scored vs Conceded</h2>
                </div>
              </div>

              <div className="analytics-chart">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={goalData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="rgba(255,255,255,0.08)"
                    />

                    <XAxis dataKey="category" stroke="#A996B0" />

                    <YAxis stroke="#A996B0" />

                    <Tooltip />

                    <Legend />

                    <Bar
                      dataKey="scored"
                      isAnimationActive={true}
                      animationDuration={800}
                      name="Scored"
                      fill={theme.primary}
                      radius={[6, 6, 0, 0]}
                    />

                    <Bar
                      dataKey="conceded"
                      isAnimationActive={true}
                      animationDuration={800}
                      name="Conceded"
                      fill="#D8CFDA"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="goal-summary">
                <div>
                  <span>Goals scored</span>
                  <strong>
                    {teamStatistics.goals_scored.toLocaleString()}
                  </strong>
                </div>

                <div>
                  <span>Goals conceded</span>
                  <strong>
                    {teamStatistics.goals_conceded.toLocaleString()}
                  </strong>
                </div>

                <div>
                  <span>Goal difference</span>
                  <strong>
                    {teamStatistics.goal_difference > 0 ? "+" : ""}
                    {teamStatistics.goal_difference.toLocaleString()}
                  </strong>
                </div>
              </div>
            </section>
          </motion.div>

          {/* ================================
            HOME VS AWAY
        ================================= */}

          <motion.section
            className="analytics-panel venue-panel"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.24 }}
          >
            <div className="card-header">
              <div>
                <p className="eyebrow">VENUE PERFORMANCE</p>

                <h2>Home vs Away</h2>
              </div>
            </div>

            <div className="analytics-chart">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={venueData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.08)"
                  />

                  <XAxis dataKey="category" stroke="#A996B0" />

                  <YAxis stroke="#A996B0" />

                  <Tooltip />

                  <Legend />

                  <Bar
                    dataKey="wins"
                    isAnimationActive={true}
                    animationDuration={800}
                    name="Wins"
                    fill="#FF6B5F"
                    radius={[6, 6, 0, 0]}
                  />

                  <Bar
                    dataKey="draws"
                    isAnimationActive={true}
                    animationDuration={800}
                    name="Draws"
                    fill="#FFC857"
                    radius={[6, 6, 0, 0]}
                  />

                  <Bar
                    dataKey="losses"
                    isAnimationActive={true}
                    animationDuration={800}
                    name="Losses"
                    fill="#48B5A5"
                    radius={[6, 6, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.section>

          {/* ================================
            HIGHLIGHT
        ================================= */}

          <motion.section
            className="analytics-highlight"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.32 }}
          >
            <div>
              <p className="eyebrow">HISTORICAL HIGHLIGHT</p>

              <h2>
                {teamStatistics.goal_difference > 0
                  ? `+${teamStatistics.goal_difference}`
                  : teamStatistics.goal_difference}{" "}
                goal difference
              </h2>

              <p>
                Across {teamStatistics.matches_played.toLocaleString()}{" "}
                historical matches, {selectedTeam} scored{" "}
                {teamStatistics.goals_scored.toLocaleString()} goals and
                conceded {teamStatistics.goals_conceded.toLocaleString()}.
              </p>
            </div>
          </motion.section>
        </div>
      </PageTransition>
    );
  }

  /*
   * =========================================
   * LEAGUE ANALYTICS
   * =========================================
   */

  if (leagueAnalytics) {
    const { overall, season_trends, team_rankings } = leagueAnalytics;

    const seasonTrendData = normalizeSeasonTrends(season_trends);

    return (
      <PageTransition>
        <div className="analytics-page league-analytics-page">
          {/* ================================
            LEAGUE HEADER
        ================================= */}

          <div className="page-header">
            <div>
              <p className="eyebrow">LEAGUE ANALYTICS</p>

              <h1>Premier League</h1>

              <p className="page-description">
                Historical league trends across{" "}
                {overall.total_matches.toLocaleString()} matches from the
                available dataset.
              </p>
            </div>
          </div>

          {/* ================================
            KPI CARDS
        ================================= */}

          <motion.div
            className="analytics-kpi-grid"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.08 }}
          >
            <div className="analytics-kpi-card">
              <span>Matches</span>

              <strong>
                <AnimatedNumber value={overall.total_matches} duration={1.2} />
              </strong>

              <small>Historical matches analyzed</small>
            </div>

            <div className="analytics-kpi-card">
              <span>Total Goals</span>

              <strong>{overall.total_goals.toLocaleString()}</strong>

              <small>Across all matches</small>
            </div>

            <div className="analytics-kpi-card">
              <span>Goals / Match</span>

              <strong>{overall.goals_per_match}</strong>

              <small>League-wide average</small>
            </div>

            <div className="analytics-kpi-card">
              <span>Home Win Rate</span>

              <strong>{overall.home_win_percentage}%</strong>

              <small>{overall.home_wins.toLocaleString()} home wins</small>
            </div>
          </motion.div>

          {/* ================================
            OUTCOME TRENDS
        ================================= */}

          <motion.section
            className="analytics-panel"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.16 }}
          >
            <div className="card-header">
              <div>
                <p className="eyebrow">SEASON TRENDS</p>

                <h2>Match Outcome Trends</h2>
              </div>
            </div>

            <div className="analytics-chart">
              <MeasuredChart height={360}>
                <LineChart
                  data={seasonTrendData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 0,
                    bottom: 10,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.08)"
                  />

                  <XAxis dataKey="season" stroke="#A996B0" />

                  <YAxis
                    domain={[0, 60]}
                    stroke="#A996B0"
                    tickFormatter={(value) => `${value}%`}
                  />

                  <Tooltip formatter={(value) => `${value}%`} />

                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="home_win_percentage"
                    isAnimationActive={true}
                    animationDuration={900}
                    animationEasing="ease-out"
                    name="Home Win"
                    stroke="#FF6B5F"
                    strokeWidth={3}
                    dot={false}
                  />

                  <Line
                    type="monotone"
                    dataKey="draw_percentage"
                    isAnimationActive={true}
                    animationDuration={900}
                    animationEasing="ease-out"
                    name="Draw"
                    stroke="#FFC857"
                    strokeWidth={3}
                    dot={false}
                  />

                  <Line
                    type="monotone"
                    dataKey="away_win_percentage"
                    isAnimationActive={true}
                    animationDuration={900}
                    animationEasing="ease-out"
                    name="Away Win"
                    stroke="#48B5A5"
                    strokeWidth={3}
                    dot={false}
                  />
                </LineChart>
              </MeasuredChart>
            </div>
          </motion.section>

          {/* ================================
            GOAL TRENDS
        ================================= */}

          <motion.div
            className="analytics-chart-grid"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.24 }}
          >
            <section className="analytics-panel">
              <div className="card-header">
                <div>
                  <p className="eyebrow">SCORING TRENDS</p>

                  <h2>Goals Per Match</h2>
                </div>
              </div>

              <div className="analytics-chart">
                <MeasuredChart height={300}>
                  <LineChart
                    data={seasonTrendData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="rgba(255,255,255,0.08)"
                    />

                    <XAxis dataKey="season" stroke="#A996B0" />

                    <YAxis stroke="#A996B0" />

                    <Tooltip />

                    <Line
                      type="monotone"
                      dataKey="goals_per_match"
                      name="Goals / Match"
                      stroke="#A96BB5"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </MeasuredChart>
              </div>
            </section>

            <section className="analytics-panel">
              <div className="card-header">
                <div>
                  <p className="eyebrow">HOME VS AWAY</p>

                  <h2>Goals by Venue</h2>
                </div>
              </div>

              <div className="analytics-chart">
                <MeasuredChart height={300}>
                  <BarChart
                    data={seasonTrendData}
                    margin={{
                      top: 10,
                      right: 10,
                      left: 0,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="rgba(255,255,255,0.08)"
                    />

                    <XAxis dataKey="season" stroke="#A996B0" />

                    <YAxis stroke="#A996B0" />

                    <Tooltip />

                    <Legend />

                    <Bar
                      dataKey="home_goals_per_match"
                      isAnimationActive={true}
                      animationDuration={850}
                      name="Home Goals"
                      fill="#FF6B5F"
                      radius={[4, 4, 0, 0]}
                    />

                    <Bar
                      dataKey="away_goals_per_match"
                      isAnimationActive={true}
                      animationDuration={850}
                      name="Away Goals"
                      fill="#48B5A5"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </MeasuredChart>
              </div>
            </section>
          </motion.div>

          {/* ================================
            HISTORICAL TEAM PERFORMANCE
        ================================= */}

          <motion.section
            className="analytics-panel"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.32 }}
          >
            <div className="card-header">
              <div>
                <p className="eyebrow">HISTORICAL PERFORMANCE</p>

                <h2>Team Performance</h2>

                <p className="panel-description">
                  Aggregate performance across the full historical dataset.
                </p>
              </div>
            </div>

            <div className="league-leaderboard">
              {team_rankings.map((team) => {
                const metadata = teamMetadata[team.team];

                return (
                  <div
                    key={team.team}
                    className="leaderboard-row"
                    style={{
                      "--team-primary": metadata?.primary || "#541E5D",
                    }}
                  >
                    {/* Rank */}
                    <div className="leaderboard-rank">
                      <span>{team.rank}</span>
                    </div>

                    {/* Team */}
                    <div className="leaderboard-team">
                      <div className="leaderboard-crest">
                        {metadata?.crest ? (
                          <img
                            src={metadata.crest}
                            alt={`${team.team} crest`}
                          />
                        ) : (
                          <span>{team.team.charAt(0)}</span>
                        )}
                      </div>

                      <div className="leaderboard-team-info">
                        <h3>{team.team}</h3>

                        <span>{team.matches} matches</span>
                      </div>
                    </div>

                    {/* Record */}
                    <div className="leaderboard-record">
                      <div className="record-label">RECORD</div>

                      <div className="record-values">
                        <span className="record-win">{team.wins}W</span>

                        <span>{team.draws}D</span>

                        <span className="record-loss">{team.losses}L</span>
                      </div>
                    </div>

                    {/* Win percentage */}
                    <div className="leaderboard-winrate">
                      <div className="winrate-header">
                        <span>WIN RATE</span>

                        <strong>{team.win_percentage}%</strong>
                      </div>

                      <div className="winrate-track">
                        <div
                          className="winrate-fill"
                          style={{
                            width: `${team.win_percentage}%`,
                          }}
                        />
                      </div>
                    </div>

                    {/* Goal difference */}
                    <div className="leaderboard-gd">
                      <span>GOAL DIFF.</span>

                      <strong
                        className={
                          team.goal_difference >= 0
                            ? "positive-value"
                            : "negative-value"
                        }
                      >
                        {team.goal_difference > 0 ? "+" : ""}
                        {team.goal_difference}
                      </strong>
                    </div>

                    {/* Points */}
                    <div className="leaderboard-points">
                      <span>POINTS</span>

                      <strong>{team.points}</strong>
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.section>
        </div>
      </PageTransition>
    );
  }

  /*
   * =========================================
   * FALLBACK
   * =========================================
   */

  return (
    <PageTransition>
      <div className="analytics-page">
        <div className="analytics-error">
          <h2>No analytics available</h2>
          <p>There is currently no analytics data available.</p>
        </div>
      </div>
    </PageTransition>
  );
}

export default Analytics;
