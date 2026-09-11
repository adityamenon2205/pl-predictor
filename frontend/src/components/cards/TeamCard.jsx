import teamMetadata from "../../data/teams";

function TeamCard({ team, onClick }) {
  const theme = teamMetadata[team] || {
    primary: "#541E5D",
    secondary: "#FFFFFF",
    accent: "#541E5D",
    crest: null,
  };

  return (
    <button
      className="team-card"
      onClick={() => onClick?.(team)}
      style={{
        "--team-primary": theme.primary,
        "--team-secondary": theme.secondary,
        "--team-accent": theme.accent,
      }}
    >
      {/* Main card background */}
      <div className="team-card-background" />

      {/* Large faded crest in background */}
      {theme.crest && (
        <img
          className="team-card-crest-bg"
          src={theme.crest}
          alt=""
          aria-hidden="true"
        />
      )}

      {/* Card content */}
      <div className="team-card-content">
        <div className="team-crest">
          {theme.crest ? (
            <img
              src={theme.crest}
              alt={`${team} crest`}
            />
          ) : (
            <div className="team-crest-fallback">
              {team.charAt(0)}
            </div>
          )}
        </div>

        <div className="team-card-info">
          <h3>{team}</h3>

          <div className="team-card-footer">
            <span>View statistics</span>

            <span className="team-arrow">
              →
            </span>
          </div>
        </div>
      </div>
    </button>
  );
}

export default TeamCard;