import { useEffect, useMemo, useState } from "react";

import { getPredictionHistory } from "../services/api";
import teamMetadata from "../data/teams";

function History() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPredictionHistory() {
      try {
        const data = await getPredictionHistory();

        setPredictions(data.predictions || []);
      } catch (err) {
        setError(err.message || "Failed to load prediction history.");
      } finally {
        setLoading(false);
      }
    }

    loadPredictionHistory();
  }, []);

  /* =========================================================
     HELPERS
     ========================================================= */

  function getOutcomeClass(outcome) {
    if (outcome === "Home Win") {
      return "history-home";
    }

    if (outcome === "Away Win") {
      return "history-away";
    }

    return "history-draw";
  }

  function getOutcomeColor(outcome) {
    if (outcome === "Home Win") {
      return "#F26B5B";
    }

    if (outcome === "Away Win") {
      return "#43B3A3";
    }

    return "#FFC857";
  }

  function getOutcomeLabel(outcome) {
    if (outcome === "Home Win") {
      return "HOME WIN";
    }

    if (outcome === "Away Win") {
      return "AWAY WIN";
    }

    return "DRAW";
  }

  function formatProbability(value) {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return "—";
    }

    return `${(numericValue * 100).toFixed(2)}%`;
  }

  function formatDate(value) {
    if (!value) {
      return "Date unavailable";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "Date unavailable";
    }

    return date.toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function getPredictionDate(prediction) {
    return (
      prediction.timestamp ||
      prediction.created_at ||
      prediction.createdAt ||
      prediction.date ||
      null
    );
  }

  function getTeamTheme(teamName) {
    return (
      teamMetadata[teamName] || {
        primary: "#541E5D",
        secondary: "#FFFFFF",
        accent: "#541E5D",
        crest: null,
      }
    );
  }

  /* =========================================================
     SORT PREDICTIONS
     Newest predictions appear first.
     Predictions without timestamps remain usable.
     ========================================================= */

  const sortedPredictions = useMemo(() => {
    return [...predictions].sort((a, b) => {
      const dateA = getPredictionDate(a);
      const dateB = getPredictionDate(b);

      if (!dateA && !dateB) {
        return 0;
      }

      if (!dateA) {
        return 1;
      }

      if (!dateB) {
        return -1;
      }

      const timeA = new Date(dateA).getTime();
      const timeB = new Date(dateB).getTime();

      if (Number.isNaN(timeA) && Number.isNaN(timeB)) {
        return 0;
      }

      if (Number.isNaN(timeA)) {
        return 1;
      }

      if (Number.isNaN(timeB)) {
        return -1;
      }

      return timeB - timeA;
    });
  }, [predictions]);

  /* =========================================================
     LOADING
     ========================================================= */

  if (loading) {
    return (
      <div className="history-page">
        <div className="history-loading">
          <div className="loading-spinner"></div>

          <p>Loading prediction history...</p>
        </div>
      </div>
    );
  }

  /* =========================================================
     ERROR
     ========================================================= */

  if (error) {
    return (
      <div className="history-page">
        <div className="page-header history-header">
          <div>
            <p className="eyebrow">PREDICTION LOG</p>

            <h1>History</h1>

            <p className="page-description">
              Review previously generated Premier League match predictions.
            </p>
          </div>
        </div>

        <div className="history-error">
          <span>⚠</span>

          <div>
            <strong>Unable to load prediction history</strong>

            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  /* =========================================================
     MAIN PAGE
     ========================================================= */

  return (
    <div className="history-page">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="page-header history-header">
        <div>
          <p className="eyebrow">PREDICTION LOG</p>

          <h1>History</h1>

          <p className="page-description">
            Review previously generated Premier League match predictions and
            their probability breakdowns.
          </p>
        </div>

        <div className="history-count">
          <span>Predictions</span>

          <strong>{predictions.length}</strong>
        </div>
      </div>

      {/* =====================================================
          EMPTY STATE
          ===================================================== */}

      {predictions.length === 0 ? (
        <div className="history-empty">
          <div className="history-empty-icon">◷</div>

          <h2>No predictions yet</h2>

          <p>
            Your predictions will appear here after you use the Match
            Predictor.
          </p>
        </div>
      ) : (
        /* ===================================================
           HISTORY LIST
           =================================================== */

        <div className="history-list">
          {sortedPredictions.map((prediction, index) => {
            const homeTeam = prediction.home_team;
            const awayTeam = prediction.away_team;

            const homeTheme = getTeamTheme(homeTeam);
            const awayTheme = getTeamTheme(awayTeam);

            const outcome = prediction.prediction;
            const outcomeColor = getOutcomeColor(outcome);
            const outcomeClass = getOutcomeClass(outcome);
            const outcomeLabel = getOutcomeLabel(outcome);

            const predictionDate = getPredictionDate(prediction);

            return (
              <article
                className="history-card"
                key={
                  prediction._id ||
                  prediction.id ||
                  `${homeTeam}-${awayTeam}-${index}`
                }
                style={{
                  "--history-outcome-color": outcomeColor,
                }}
              >
                {/* =================================================
                    MATCH
                    ================================================= */}

                <div className="history-match">
                  {/* HOME TEAM */}

                  <div className="history-team">
                    <div
                      className="history-team-crest"
                      style={{
                        "--team-primary": homeTheme.primary,
                      }}
                    >
                      {homeTheme.crest ? (
                        <img
                          src={homeTheme.crest}
                          alt={`${homeTeam} crest`}
                        />
                      ) : (
                        <span>{homeTeam?.charAt(0)}</span>
                      )}
                    </div>

                    <div>
                      <span className="history-team-label">HOME</span>

                      <strong>{homeTeam}</strong>
                    </div>
                  </div>

                  {/* VS */}

                  <div className="history-vs">VS</div>

                  {/* AWAY TEAM */}

                  <div className="history-team history-team-away">
                    <div
                      className="history-team-crest"
                      style={{
                        "--team-primary": awayTheme.primary,
                      }}
                    >
                      {awayTheme.crest ? (
                        <img
                          src={awayTheme.crest}
                          alt={`${awayTeam} crest`}
                        />
                      ) : (
                        <span>{awayTeam?.charAt(0)}</span>
                      )}
                    </div>

                    <div>
                      <span className="history-team-label">AWAY</span>

                      <strong>{awayTeam}</strong>
                    </div>
                  </div>
                </div>

                {/* =================================================
                    PREDICTED OUTCOME
                    ================================================= */}

                <div className="history-outcome">
                  <span className="history-outcome-label">
                    PREDICTED RESULT
                  </span>

                  <strong className={outcomeClass}>{outcomeLabel}</strong>
                </div>

                {/* =================================================
                    PROBABILITY BREAKDOWN
                    ================================================= */}

                <div className="history-probabilities">
                  {/* HOME */}

                  <div className="history-probability">
                    <span>
                      <i className="history-dot home"></i>
                      Home
                    </span>

                    <strong>
                      {formatProbability(prediction.probabilities?.home)}
                    </strong>
                  </div>

                  {/* DRAW */}

                  <div className="history-probability">
                    <span>
                      <i className="history-dot draw"></i>
                      Draw
                    </span>

                    <strong>
                      {formatProbability(prediction.probabilities?.draw)}
                    </strong>
                  </div>

                  {/* AWAY */}

                  <div className="history-probability">
                    <span>
                      <i className="history-dot away"></i>
                      Away
                    </span>

                    <strong>
                      {formatProbability(prediction.probabilities?.away)}
                    </strong>
                  </div>
                </div>

                {/* =================================================
                    DATE
                    ================================================= */}

                <div
                  className="history-date"
                  style={{
                    "--outcome-color": outcomeColor,
                  }}
                >
                  {formatDate(predictionDate)}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default History;