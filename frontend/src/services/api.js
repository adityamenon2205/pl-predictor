const API_BASE_URL = "http://127.0.0.1:8000";

export async function getStatistics() {
  const response = await fetch(`${API_BASE_URL}/statistics/`);

  if (!response.ok) {
    throw new Error("Failed to fetch statistics");
  }

  return response.json();
}

export async function getTeams() {
  const response = await fetch(`${API_BASE_URL}/teams/`);

  if (!response.ok) {
    throw new Error("Failed to fetch teams");
  }

  return response.json();
}

export async function getTeamStatistics(teamName) {
  const response = await fetch(
    `${API_BASE_URL}/teams/${encodeURIComponent(teamName)}/statistics`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch team statistics");
  }

  return response.json();
}

export async function predictMatch(homeTeam, awayTeam) {
  const response = await fetch(`${API_BASE_URL}/predict/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      home_team: homeTeam,
      away_team: awayTeam,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);

    throw new Error(
      errorData?.detail || "Failed to predict match"
    );
  }

  return response.json();
}