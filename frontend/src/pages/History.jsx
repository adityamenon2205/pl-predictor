
import { useEffect, useMemo, useState } from "react";
import { motion } from "motion/react";

import "./HistoryModal.css";

import {
  getPredictionHistory,
  clearPredictionHistory,
} from "../services/api";

import teamMetadata from "../data/teams";
import PageTransition from "../components/common/PageTransition";

function History() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [clearing, setClearing] = useState(false);
  const [clearError, setClearError] = useState(null);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  // Load prediction history
  useEffect(() => {
    async function loadPredictionHistory() {
      try {
        const data = await getPredictionHistory();
        setPredictions(data.predictions || []);
      } catch (err) {
        setError(
          err.message || "Failed to load prediction history."
        );
      } finally {
        setLoading(false);
      }
    }

    loadPredictionHistory();
  }, []);

  // Clear prediction history after confirmation
  async function handleClearHistory() {
    if (predictions.length === 0 || clearing) {
      return;
    }

    setClearing(true);
    setClearError(null);

    try {
      await clearPredictionHistory();

      // Update the UI only after successful deletion.
      setPredictions([]);
      setError(null);
      setShowClearConfirm(false);
    } catch (err) {
      setClearError(
        err.message || "Failed to clear prediction history."
      );
      setShowClearConfirm(false);
    } finally {
      setClearing(false);
    }
  }

  // Outcome styling
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

  // Format probabilities
  function formatProbability(value) {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return "—";
    }

    return `${(numericValue * 100).toFixed(2)}%`;
  }

  // Format prediction date
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

  // Get team colours and crest
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

  // Sort newest predictions first
  const sortedPredictions = useMemo(() => {
    return [...predictions].sort((a, b) => {
      const dateA = getPredictionDate(a);
      const dateB = getPredictionDate(b);

      if (!dateA && !dateB) return 0;
      if (!dateA) return 1;
      if (!dateB) return -1;

      const timeA = new Date(dateA).getTime();
      const timeB = new Date(dateB).getTime();

      if (Number.isNaN(timeA) && Number.isNaN(timeB)) {
        return 0;
      }

      if (Number.isNaN(timeA)) return 1;
      if (Number.isNaN(timeB)) return -1;

      return timeB - timeA;
    });
  }, [predictions]);

  // History card animations
  const historyListVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.07,
      },
    },
  };

  const historyCardVariants = {
    hidden: {
      opacity: 0,
      y: 14,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.35,
        ease: [0.22, 1, 0.36, 1],
      },
    },
  };

  // Loading state
  if (loading) {
    return (
      <PageTransition>
        <div className="history-page">
          <div className="history-loading">
            <div className="loading-spinner" />
            <p>Loading prediction history...</p>
          </div>
        </div>
      </PageTransition>
    );
  }

  // Error state
  if (error) {
    return (
      <PageTransition>
        <div className="history-page">
          <div className="page-header history-header">
            <div>
              <p className="eyebrow">PREDICTION LOG</p>
              <h1>History</h1>
              <p className="page-description">
                Review previously generated Premier League match
                predictions.
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
      </PageTransition>
    );
  }

  // Main page
  return (
    <PageTransition>
      <div className="history-page">
        {/* HEADER */}
        <div className="page-header history-header">
          <div>
            <p className="eyebrow">PREDICTION LOG</p>
            <h1>History</h1>
            <p className="page-description">
              Review previously generated Premier League match
              predictions and their probability breakdowns.
            </p>
          </div>

          <div className="history-header-actions">
            <div className="history-count">
              <span>Predictions</span>
              <strong>{predictions.length}</strong>
            </div>

            {predictions.length > 0 && (
              <button
                type="button"
                className="clear-history-button"
                onClick={() => {
                  setClearError(null);
                  setShowClearConfirm(true);
                }}
                disabled={clearing}
              >
                <span aria-hidden="true">⌫</span>
                Clear History
              </button>
            )}
          </div>
        </div>

        {/* CLEAR HISTORY ERROR */}
        {clearError && (
          <div className="history-error" role="alert">
            <span aria-hidden="true">⚠</span>
            <div>
              <strong>
                Unable to clear prediction history
              </strong>
              <p>{clearError}</p>
            </div>
          </div>
        )}

        {/* EMPTY STATE OR HISTORY LIST */}
        {predictions.length === 0 ? (
          <div className="history-empty">
            <div className="history-empty-icon">◷</div>
            <h2>No predictions yet</h2>
            <p>
              Your predictions will appear here after you use
              the Match Predictor.
            </p>
          </div>
        ) : (
          <motion.div
            className="history-list"
            variants={historyListVariants}
            initial="hidden"
            animate="visible"
          >
            {sortedPredictions.map((prediction, index) => {
              const homeTeam = prediction.home_team;
              const awayTeam = prediction.away_team;

              const homeTheme = getTeamTheme(homeTeam);
              const awayTheme = getTeamTheme(awayTeam);

              const outcome = prediction.prediction;
              const outcomeColor = getOutcomeColor(outcome);
              const outcomeClass = getOutcomeClass(outcome);
              const outcomeLabel = getOutcomeLabel(outcome);

              const predictionDate =
                getPredictionDate(prediction);

              return (
                <motion.article
                  className="history-card"
                  key={
                    prediction._id ||
                    prediction.id ||
                    `${homeTeam}-${awayTeam}-${index}`
                  }
                  variants={historyCardVariants}
                  style={{
                    "--history-outcome-color": outcomeColor,
                  }}
                >
                  {/* MATCH */}
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
                        <span className="history-team-label">
                          HOME
                        </span>
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
                        <span className="history-team-label">
                          AWAY
                        </span>
                        <strong>{awayTeam}</strong>
                      </div>
                    </div>
                  </div>

                  {/* PREDICTED OUTCOME */}
                  <div className="history-outcome">
                    <span className="history-outcome-label">
                      PREDICTED RESULT
                    </span>
                    <strong className={outcomeClass}>
                      {outcomeLabel}
                    </strong>
                  </div>

                  {/* PROBABILITY BREAKDOWN */}
                  <div className="history-probabilities">
                    <div className="history-probability">
                      <span>
                        <i className="history-dot home" />
                        Home
                      </span>
                      <strong>
                        {formatProbability(
                          prediction.probabilities?.home
                        )}
                      </strong>
                    </div>

                    <div className="history-probability">
                      <span>
                        <i className="history-dot draw" />
                        Draw
                      </span>
                      <strong>
                        {formatProbability(
                          prediction.probabilities?.draw
                        )}
                      </strong>
                    </div>

                    <div className="history-probability">
                      <span>
                        <i className="history-dot away" />
                        Away
                      </span>
                      <strong>
                        {formatProbability(
                          prediction.probabilities?.away
                        )}
                      </strong>
                    </div>
                  </div>

                  {/* DATE */}
                  <div
                    className="history-date"
                    style={{
                      "--outcome-color": outcomeColor,
                    }}
                  >
                    {formatDate(predictionDate)}
                  </div>
                </motion.article>
              );
            })}
          </motion.div>
        )}

        {/* CUSTOM CLEAR HISTORY CONFIRMATION MODAL */}
        {showClearConfirm && (
          <div
            className="history-modal-backdrop"
            onClick={() => {
              if (!clearing) {
                setShowClearConfirm(false);
              }
            }}
          >
            <motion.div
              className="history-confirm-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="clear-history-title"
              aria-describedby="clear-history-description"
              initial={{
                opacity: 0,
                scale: 0.94,
                y: 12,
              }}
              animate={{
                opacity: 1,
                scale: 1,
                y: 0,
              }}
              transition={{ duration: 0.2 }}
              onClick={(event) => event.stopPropagation()}
            >
              <div className="history-modal-icon">
                <span aria-hidden="true">!</span>
              </div>

              <p className="history-modal-eyebrow">
                PERMANENT ACTION
              </p>

              <h2 id="clear-history-title">
                Clear prediction history?
              </h2>

              <p
                id="clear-history-description"
                className="history-modal-description"
              >
                You're about to delete all{" "}
                <strong>{predictions.length}</strong>{" "}
                saved predictions. This action cannot be undone.
              </p>

              <div className="history-modal-summary">
                <span>Predictions to delete</span>
                <strong>{predictions.length}</strong>
              </div>

              <div className="history-modal-actions">
                <button
                  type="button"
                  className="history-modal-cancel"
                  onClick={() => setShowClearConfirm(false)}
                  disabled={clearing}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="history-modal-delete"
                  onClick={handleClearHistory}
                  disabled={clearing}
                >
                  {clearing ? (
                    <>
                      <span className="clear-history-spinner" />
                      Clearing...
                    </>
                  ) : (
                    "Yes, clear history"
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </PageTransition>
  );
}

export default History;
