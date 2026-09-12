import { useEffect, useState } from "react";

import { getTeams, predictMatch } from "../services/api";
import teamMetadata from "../data/teams";

function TeamSearch({
  label,
  value,
  onChange,
  teams,
  placeholder,
  disabledTeam,
}) {
  const [search, setSearch] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const filteredTeams = teams.filter((team) =>
    team.toLowerCase().includes(search.toLowerCase())
  );

  function handleSelect(team) {
    onChange(team);
    setSearch("");
    setIsOpen(false);
  }

  function handleInputChange(event) {
    setSearch(event.target.value);
    setIsOpen(true);

    if (value) {
      onChange("");
    }
  }

  return (
    <div className="team-selector">
      <label>{label}</label>

      <div className="team-search-wrapper">
        <input
          type="text"
          value={value || search}
          placeholder={placeholder}
          onFocus={() => setIsOpen(true)}
          onChange={handleInputChange}
          autoComplete="off"
        />

        <span className="team-search-arrow">
          {isOpen ? "⌃" : "⌄"}
        </span>

        {isOpen && (
          <div className="team-search-dropdown">
            {filteredTeams.length > 0 ? (
              filteredTeams.map((team) => {
                const isDisabled = team === disabledTeam;

                return (
                  <button
                    key={team}
                    type="button"
                    className={`team-search-option ${
                      isDisabled ? "disabled" : ""
                    } ${team === value ? "selected" : ""}`}
                    disabled={isDisabled}
                    onMouseDown={(event) => {
                      event.preventDefault();

                      if (!isDisabled) {
                        handleSelect(team);
                      }
                    }}
                  >
                    <span>{team}</span>

                    {team === value && (
                      <span className="team-selected-check">
                        ✓
                      </span>
                    )}
                  </button>
                );
              })
            ) : (
              <div className="team-search-empty">
                No teams found
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Predictor() {
  const [teams, setTeams] = useState([]);
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");

  const [prediction, setPrediction] = useState(null);

  const [loadingTeams, setLoadingTeams] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadTeams() {
      try {
        const data = await getTeams();
        setTeams(data.teams);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoadingTeams(false);
      }
    }

    loadTeams();
  }, []);

  async function handlePrediction(event) {
    event.preventDefault();

    if (!homeTeam || !awayTeam) {
      setError("Please select both teams.");
      return;
    }

    if (homeTeam === awayTeam) {
      setError("Home and away teams must be different.");
      return;
    }

    setError(null);
    setPrediction(null);
    setPredicting(true);

    try {
      const result = await predictMatch(homeTeam, awayTeam);
      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setPredicting(false);
    }
  }

  function getOutcomeClass(outcome) {
    if (outcome === "Home Win") {
      return "prediction-home";
    }

    if (outcome === "Away Win") {
      return "prediction-away";
    }

    return "prediction-draw";
  }

  function getProbabilityColor(type) {
    if (type === "home") {
      return "#F26B5B";
    }

    if (type === "draw") {
      return "#FFC857";
    }

    return "#43B3A3";
  }

  /*
   * Determine the winning team.
   *
   * Home Win  → home team
   * Away Win  → away team
   * Draw      → no single winning team
   */
  const winningTeam =
    prediction?.prediction === "Home Win"
      ? prediction.home_team
      : prediction?.prediction === "Away Win"
      ? prediction.away_team
      : null;

  const winningTeamTheme = winningTeam
    ? teamMetadata[winningTeam]
    : null;

  const homeTeamTheme = prediction
    ? teamMetadata[prediction.home_team]
    : null;

  const awayTeamTheme = prediction
    ? teamMetadata[prediction.away_team]
    : null;

  if (loadingTeams) {
    return (
      <div className="predictor-page">
        <div className="predictor-loading">
          <div className="loading-spinner"></div>
          <p>Loading teams...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="predictor-page">
      {/* Header */}

      <div className="page-header predictor-header">
        <div>
          <p className="eyebrow">MACHINE LEARNING</p>

          <h1>Match Predictor</h1>

          <p className="page-description">
            Predict the outcome of a Premier League fixture
            using the trained Random Forest model.
          </p>
        </div>
      </div>

      {/* Predictor Form */}

      <section className="dashboard-card predictor-form-card">
        <div className="card-header">
          <div>
            <p className="eyebrow">FIXTURE</p>
            <h2>Select Teams</h2>
          </div>
        </div>

        <form onSubmit={handlePrediction}>
          <div className="predictor-matchup">
            {/* Home Team */}

            <TeamSearch
              label="Home Team"
              value={homeTeam}
              onChange={(team) => {
                setHomeTeam(team);
                setPrediction(null);
                setError(null);
              }}
              teams={teams}
              placeholder="Search home team..."
              disabledTeam={awayTeam}
            />

            {/* VS */}

            <div className="vs-divider">
              <span>VS</span>
            </div>

            {/* Away Team */}

            <TeamSearch
              label="Away Team"
              value={awayTeam}
              onChange={(team) => {
                setAwayTeam(team);
                setPrediction(null);
                setError(null);
              }}
              teams={teams}
              placeholder="Search away team..."
              disabledTeam={homeTeam}
            />
          </div>

          {error && (
            <div className="predictor-error">
              <span>⚠</span>
              <p>{error}</p>
            </div>
          )}

          <button
            type="submit"
            className="predict-button"
            disabled={predicting}
          >
            {predicting ? (
              <>
                <span className="button-spinner"></span>
                Predicting...
              </>
            ) : (
              <>
                Predict Match
                <span>→</span>
              </>
            )}
          </button>
        </form>
      </section>

      {/* =========================================
          PREDICTION RESULT
          ========================================= */}

      {prediction && (
        <section className="dashboard-card prediction-result-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">MODEL PREDICTION</p>
              <h2>Predicted Outcome</h2>
            </div>
          </div>

          <div className="prediction-result">
            {/* Match */}

            <div className="prediction-match">
              <div className="prediction-team-name">
                <span>{prediction.home_team}</span>
              </div>

              <strong>vs</strong>

              <div className="prediction-team-name">
                <span>{prediction.away_team}</span>
              </div>
            </div>

            {/* =====================================
                HOME / AWAY WIN
                ===================================== */}

            {winningTeamTheme && (
              <div
                className={`prediction-outcome ${getOutcomeClass(
                  prediction.prediction
                )}`}
                style={{
                  "--winning-primary":
                    winningTeamTheme.primary,
                  "--winning-secondary":
                    winningTeamTheme.secondary,
                  "--winning-accent":
                    winningTeamTheme.accent,
                }}
              >
                <div className="prediction-winning-crest">
                  {winningTeamTheme.crest ? (
                    <img
                      src={winningTeamTheme.crest}
                      alt={`${winningTeam} crest`}
                    />
                  ) : (
                    <span>
                      {winningTeam.charAt(0)}
                    </span>
                  )}
                </div>

                <span className="prediction-label">
                  PREDICTED RESULT
                </span>

                <strong>{prediction.prediction}</strong>

                <span className="prediction-winning-team">
                  {winningTeam}
                </span>
              </div>
            )}

            {/* =====================================
                DRAW
                ===================================== */}

            {prediction.prediction === "Draw" && (
              <div
                className="prediction-outcome prediction-draw prediction-draw-result"
                style={{
                  "--home-primary":
                    homeTeamTheme?.primary ||
                    "#541E5D",
                  "--away-primary":
                    awayTeamTheme?.primary ||
                    "#541E5D",
                }}
              >
                <div className="draw-crests">
                  <div className="draw-crest draw-crest-home">
                    {homeTeamTheme?.crest ? (
                      <img
                        src={homeTeamTheme.crest}
                        alt={`${prediction.home_team} crest`}
                      />
                    ) : (
                      <span>
                        {prediction.home_team.charAt(0)}
                      </span>
                    )}
                  </div>

                  <div className="draw-vs">
                    +
                  </div>

                  <div className="draw-crest draw-crest-away">
                    {awayTeamTheme?.crest ? (
                      <img
                        src={awayTeamTheme.crest}
                        alt={`${prediction.away_team} crest`}
                      />
                    ) : (
                      <span>
                        {prediction.away_team.charAt(0)}
                      </span>
                    )}
                  </div>
                </div>

                <span className="prediction-label">
                  PREDICTED RESULT
                </span>

                <strong>Draw</strong>

                <span className="prediction-winning-team">
                  Both teams share the result
                </span>
              </div>
            )}
          </div>

          {/* =====================================
              PROBABILITY BREAKDOWN
              ===================================== */}

          <div className="probability-section">
            <div className="probability-header">
              <div>
                <p className="eyebrow">
                  PROBABILITY BREAKDOWN
                </p>

                <h3>Model Confidence</h3>
              </div>
            </div>

            <div className="probability-grid">
              {/* Home */}

              <div className="probability-card">
                <div className="probability-card-header">
                  <span
                    className="probability-dot"
                    style={{
                      background:
                        getProbabilityColor("home"),
                    }}
                  ></span>

                  <span>Home Win</span>
                </div>

                <strong>
                  {(
                    prediction.probabilities.home * 100
                  ).toFixed(2)}
                  %
                </strong>

                <div className="probability-bar">
                  <div
                    className="probability-fill home"
                    style={{
                      width: `${
                        prediction.probabilities.home * 100
                      }%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Draw */}

              <div className="probability-card">
                <div className="probability-card-header">
                  <span
                    className="probability-dot"
                    style={{
                      background:
                        getProbabilityColor("draw"),
                    }}
                  ></span>

                  <span>Draw</span>
                </div>

                <strong>
                  {(
                    prediction.probabilities.draw * 100
                  ).toFixed(2)}
                  %
                </strong>

                <div className="probability-bar">
                  <div
                    className="probability-fill draw"
                    style={{
                      width: `${
                        prediction.probabilities.draw * 100
                      }%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Away */}

              <div className="probability-card">
                <div className="probability-card-header">
                  <span
                    className="probability-dot"
                    style={{
                      background:
                        getProbabilityColor("away"),
                    }}
                  ></span>

                  <span>Away Win</span>
                </div>

                <strong>
                  {(
                    prediction.probabilities.away * 100
                  ).toFixed(2)}
                  %
                </strong>

                <div className="probability-bar">
                  <div
                    className="probability-fill away"
                    style={{
                      width: `${
                        prediction.probabilities.away * 100
                      }%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

export default Predictor;