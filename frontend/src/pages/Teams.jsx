import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { useNavigate } from "react-router-dom";

import { getTeams } from "../services/api";
import TeamCard from "../components/cards/TeamCard";
import PageTransition from "../components/common/PageTransition";

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

  /* =========================================================
     TEAM CARD ANIMATION
     ========================================================= */

  const teamGridVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.055,
      },
    },
  };

  const teamCardVariants = {
    hidden: {
      opacity: 0,
      y: 16,
      scale: 0.98,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.35,
        ease: [0.22, 1, 0.36, 1],
      },
    },
  };

  /* =========================================================
     LOADING
     ========================================================= */

  if (loading) {
    return (
      <PageTransition>
        <div className="teams-page">
          <h1>Teams</h1>
          <p>Loading teams...</p>
        </div>
      </PageTransition>
    );
  }

  /* =========================================================
     ERROR
     ========================================================= */

  if (error) {
    return (
      <PageTransition>
        <div className="teams-page">
          <h1>Teams</h1>
          <p>Unable to load teams.</p>
          <span>{error}</span>
        </div>
      </PageTransition>
    );
  }

  /* =========================================================
     MAIN PAGE
     ========================================================= */

  return (
    <PageTransition>
      <div className="teams-page">
        {/* =====================================================
            HEADER
            ===================================================== */}

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

        {/* =====================================================
            SEARCH
            ===================================================== */}

        <div className="team-search">
          <input
            type="text"
            placeholder="Search teams..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        {/* =====================================================
            TEAM GRID
            ===================================================== */}

        <motion.div
          className="teams-grid"
          variants={teamGridVariants}
          initial="hidden"
          animate="visible"
        >
          {filteredTeams.map((team) => (
            <motion.div
              key={team}
              variants={teamCardVariants}
              style={{
                width: "100%",
              }}
            >
              <TeamCard
                team={team}
                onClick={(selectedTeam) => {
                  navigate(
                    `/analytics?team=${encodeURIComponent(
                      selectedTeam
                    )}`
                  );
                }}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* =====================================================
            EMPTY STATE
            ===================================================== */}

        {filteredTeams.length === 0 && (
          <div className="empty-state">
            <h2>No teams found</h2>
            <p>Try a different search term.</p>
          </div>
        )}
      </div>
    </PageTransition>
  );
}

export default Teams;