import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getTeams } from "../services/api";
import TeamCard from "../components/cards/TeamCard";

function Teams() {
  const navigate = useNavigate();

  const [teams, setTeams] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadTeams() {
      try {
        const data = await getTeams();
        setTeams(data.teams);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadTeams();
  }, []);

  const filteredTeams = teams.filter((team) =>
    team.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="teams-page">
        <h1>Teams</h1>
        <p>Loading teams...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="teams-page">
        <h1>Teams</h1>
        <p>Unable to load teams.</p>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="teams-page">
      <div className="page-header">
        <div>
          <p className="eyebrow">PREMIER LEAGUE</p>

          <h1>Teams</h1>

          <p className="page-description">
            Explore teams and their historical performance.
          </p>
        </div>

        <div className="team-count">
          <strong>{teams.length}</strong>
          <span>teams</span>
        </div>
      </div>

      <div className="team-search">
        <input
          type="text"
          placeholder="Search teams..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <div className="teams-grid">
        {filteredTeams.map((team) => (
          <TeamCard
            key={team}
            team={team}
            onClick={(selectedTeam) => {
              navigate(
                `/analytics?team=${encodeURIComponent(selectedTeam)}`
              );
            }}
          />
        ))}
      </div>

      {filteredTeams.length === 0 && (
        <div className="empty-state">
          <h2>No teams found</h2>
          <p>Try a different search term.</p>
        </div>
      )}
    </div>
  );
}

export default Teams;