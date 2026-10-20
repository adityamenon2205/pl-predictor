# ⚽ Premier League Match Predictor

A full-stack football analytics platform combining a machine-learning
prediction pipeline with a React dashboard, FastAPI backend, and MongoDB
Atlas.

The system predicts Premier League fixtures as **Home Win**, **Draw**,
or **Away Win** using historical match data and engineered
team-performance features, including recent form, Elo ratings, home/away
statistics, rest days, and betting-market information.

> **Current status:** Core ML, backend, database, dashboard, analytics,
> prediction history, responsive layouts, branding, page transitions,
> micro-interactions, and an in-app Clear History confirmation modal are
> implemented. The project is in the final QA, refinement, cleanup, and
> documentation stage.

------------------------------------------------------------------------

## Overview

The current production baseline is **Random Forest V4**, evaluated with
a chronological train/test split to reduce future-information leakage.

### Model performance

Held-out test season: **2025/26** (380 matches).

  Metric               Result
  -------------- ------------
  Accuracy         **50.00%**
  Log Loss             1.0315
  Macro F1             0.3792
  Draw F1              0.0189
  Test matches            380

### Model comparison

  Model                      Accuracy     Macro F1      Draw F1
  ---------------------- ------------ ------------ ------------
  **Random Forest V4**     **50.00%**       0.3792       0.0189
  Balanced XGBoost V4          43.68%   **0.3819**   **0.1410**
  Poisson V5                   48.68%       0.3621       0.0000

Random Forest V4 is the production baseline because it achieved the
highest overall accuracy on the held-out season. Draw prediction remains
a known weakness. Model experimentation is paused while application
polish is completed.

## Evaluation methodology

-   **Training seasons:** 2010/11--2024/25
-   **Held-out test season:** 2025/26
-   **Test size:** 380 matches
-   **Excluded:** 2026/27, because available data is incomplete

The processed historical dataset contains **6,080 completed matches
across 16 seasons**, from 2010/11 through 2025/26. The 2025/26 season is
reserved for held-out evaluation.

## Machine learning

The final V4 feature set contains **100 model features**, including:

-   Recent form over the previous 3, 5, and 10 matches
-   Points per game and win rates
-   Goals scored, conceded, and goal difference
-   Shots, shots on target, corners, fouls, yellow cards, and red cards
-   Home/away performance splits
-   Elo ratings and rest days
-   Relative team-strength and team-balance features
-   Betting-market implied probabilities and market margins

Rolling and historical features are generated using information
available **before the current match** to help prevent future
information leakage. Historical match data is sourced from
**Football-Data.co.uk**.

## Architecture

``` text
Football-Data.co.uk
        |
        v
Data preprocessing
        |
        v
Feature engineering (100 features)
        |
        v
Random Forest V4
        |
        v
FastAPI backend <----> MongoDB Atlas
        |
        v
React + Vite dashboard
        +-- Overview
        +-- Teams Explorer
        +-- Predictor
        +-- Team Analytics
        +-- League Analytics
        +-- Prediction History
```

## Backend API

The backend uses FastAPI, Uvicorn, Pydantic, PyMongo, and python-dotenv.

  ---------------------------------------------------------------------------------
  Method                  Endpoint                          Purpose
  ----------------------- --------------------------------- -----------------------
  GET                     `/`                               API status

  GET                     `/health`                         Health check

  GET                     `/teams/`                         Retrieve available
                                                            teams

  GET                     `/teams/{team_name}/statistics`   Statistics for a
                                                            specific team

  GET                     `/statistics/`                    League statistics

  GET                     `/statistics/league`              League-wide analytics

  POST                    `/predict/`                       Generate a match
                                                            prediction

  GET                     `/predictions/`                   Retrieve saved
                                                            prediction history

  DELETE                  `/predictions/`                   Delete saved
                                                            prediction-history
                                                            records
  ---------------------------------------------------------------------------------

### Example prediction request

``` json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea"
}
```

### Example prediction response

``` json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea",
  "prediction": "Home Win",
  "probabilities": {
    "home": 0.4107,
    "draw": 0.3518,
    "away": 0.2375
  }
}
```

The prediction service loads the trained model, generates the 100
required features through the feature service, predicts the outcome and
probabilities, and stores the result in MongoDB.

## MongoDB Atlas

Database: `pl_predictor`

  ------------------------------------------------------------------------
  Collection            Purpose                            Current records
  --------------------- --------------------- ----------------------------
  `matches`             Historical Premier                           6,080
                        League match dataset  

  `teams`               Unique teams in the                             41
                        dataset               

  `predictions`         Predictions generated   Changes as predictions are
                        through `/predict/`                           made
  ------------------------------------------------------------------------

Each prediction stores the home team, away team, predicted outcome,
home/draw/away probabilities, and timestamp.

### Clearing prediction history

The History page retrieves records using `GET /predictions/`. The
`DELETE /predictions/` endpoint deletes documents from the
**`predictions` collection only** and returns a success message and the
number of records deleted. It does not delete `matches` or `teams`.

The frontend asks for confirmation through a custom in-app modal before
making the DELETE request. The modal shows the number of records, offers
Cancel and confirmation actions, and displays a loading state while the
request runs. The page updates only after a successful API response; on
failure, an error message is displayed. Clearing history is permanent.

## Frontend and dashboard

The frontend uses React, Vite, JavaScript, React Router, Recharts,
Motion, and CSS. API requests are centralized in `src/services/api.js`.

### Overview

-   Total matches and teams
-   Home/draw/away outcome percentages
-   Outcome distribution visualization
-   Dataset snapshot
-   Animated KPI values

### Teams Explorer

-   Searchable cards for the dataset's **41 teams**
-   Team crests and club-inspired colour themes
-   Hover effects and card animations
-   Navigation to team analytics
-   Statistics retrieved from the backend

### Predictor

-   Searchable home and away team selectors
-   Crest-enhanced team selection
-   Predicted outcome and probability breakdown
-   Team-specific result styling and animated presentation
-   Predictions saved to MongoDB for history

### Team Analytics

-   Matches, wins, draws, losses, and percentages
-   Goals scored/conceded and goal difference
-   Home and away records
-   Result distribution and goals comparison charts
-   Historical highlights and animated KPIs

### League Analytics

-   Total matches, total goals, goals per match, and home win rate
-   Season-by-season result and goal trends
-   Home/away goals comparison
-   Historical team performance table and rankings
-   Responsive charts and animated KPIs

### Prediction History

-   Prediction count and history cards
-   Team crests, predicted outcome, probabilities, and timestamps
-   Loading, error, and empty states
-   Responsive layout and page transitions
-   Clear History button and custom confirmation modal
-   Loading and error feedback for the delete operation
-   Empty state displayed after successful deletion

## UI, branding, and responsive design

The primary brand colour is `#541E5D`, supported by deep purple
backgrounds, gradients, translucent surfaces, rounded cards, subtle
borders, white/off-white typography, and club-inspired team colours.

Branding includes a custom PL Predictor logo, sidebar artwork, browser
favicon, and `PL Predictor` browser-tab title.

Motion-based interactions include page entrance transitions, animated
KPI values, team-card and crest hover effects, button feedback, and
prediction-result presentation. Reduced-motion handling is included.

### Responsive layout

-   Desktop dashboard layout and fixed sidebar
-   Main content offset to account for the desktop sidebar
-   Mobile navigation layout with the desktop offset removed
-   Responsive team grids, dashboard cards, and predictor/history
    layouts
-   Responsive analytics charts and mobile chart sizing
-   Horizontal overflow prevention and touch-friendly interactions
-   Custom history modal sized for narrow viewports

## Project structure

``` text
pl-predictor/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/ (prediction.py, predictions.py, statistics.py, teams.py)
│       ├── database/ (db_collections.py, mongodb.py, seed.py)
│       ├── models/
│       ├── schemas/
│       └── services/ (container.py, feature_service.py, prediction_history_service.py, prediction_service.py, statistics_service.py)
├── frontend/
│   ├── public/ (PL Predictor logos and favicon)
│   └── src/
│       ├── components/ (cards, charts, common, layout)
│       ├── data/teams.js
│       ├── pages/ (Overview.jsx, Teams.jsx, Predictor.jsx, Analytics.jsx, History.jsx)
│       ├── services/api.js
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       └── main.jsx
├── ml/
│   ├── config.py
│   ├── data/ (raw, processed)
│   ├── models/
│   ├── notebooks/
│   ├── preprocessing/
│   └── training/
├── .gitignore
└── README.md
```

The exact set of generated model files and data files may vary. Trained
model binaries, generated datasets, environment files, and other
private/generated files are excluded from version control according to
`.gitignore`. If `HistoryModal.css` is maintained as a separate
stylesheet, it belongs under `frontend/src/pages/` and must be imported
by `History.jsx`.

## Technology stack

-   **Machine learning:** Python, Pandas, NumPy, scikit-learn, XGBoost,
    Joblib
-   **Backend:** FastAPI, Uvicorn, Pydantic, PyMongo, python-dotenv
-   **Database:** MongoDB Atlas
-   **Frontend:** React, Vite, JavaScript, React Router, Recharts,
    Motion, CSS
-   **Development:** Git, GitHub, Jupyter Notebook, VS Code

## Running the project

### 1. Start the backend

From the project root:

``` bash
cd backend
```

Activate the virtual environment if required. For Git Bash on Windows:

``` bash
source ../.venv/Scripts/activate
```

Start FastAPI:

``` bash
uvicorn app.main:app --reload
```

-   API: `http://127.0.0.1:8000`
-   Swagger documentation: `http://127.0.0.1:8000/docs`

### 2. Start the frontend

Open a second terminal:

``` bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Database and environment setup

Configure the backend using environment variables:

``` env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=pl_predictor
```

Keep `.env` out of version control. Never commit real credentials to
GitHub.

To seed the historical match data:

``` bash
cd backend
python -m app.database.seed
```

The seed process populates the `matches` and `teams` collections.
Prediction records are written to `predictions` when predictions are
generated.

## Application data flow

### Prediction workflow

``` text
User selects teams -> React Predictor -> POST /predict/ -> FastAPI
-> Prediction Service -> Feature Service -> 100 engineered features
-> Random Forest V4 -> Prediction and probabilities -> MongoDB Atlas
-> FastAPI response -> React prediction result
```

### Prediction history workflow

``` text
Prediction saved to MongoDB
  -> GET /predictions/
  -> React History page
  -> User selects Clear History
  -> In-app confirmation modal
  -> DELETE /predictions/
  -> Delete prediction documents
  -> Updated count and empty state
```

### Analytics workflow

``` text
MongoDB match data -> Statistics Service -> Statistics API
-> React Analytics dashboard -> League Analytics and Team Analytics
```

## Development status

### Machine learning

-   [x] Historical data collection and cleaning
-   [x] Feature engineering and rolling form features
-   [x] Elo ratings and home/away statistics
-   [x] Betting-market and team-difference features
-   [x] Random Forest, XGBoost, and Poisson experiments
-   [x] Chronological evaluation
-   [x] Random Forest V4 production baseline
-   [x] 2025/26 held-out evaluation
-   [x] Exclusion of incomplete 2026/27 data
-   [ ] Future model optimization

### Backend and database

-   [x] FastAPI application and APIs
-   [x] Prediction, team, and statistics services
-   [x] Prediction history retrieval and deletion
-   [x] MongoDB Atlas integration
-   [x] Matches, teams, and predictions collections
-   [x] Database seeding and prediction persistence
-   [x] CORS configuration

### Frontend

-   [x] React + Vite setup and React Router
-   [x] Application layout, sidebar, branding, and favicon
-   [x] Overview dashboard and real backend statistics
-   [x] Teams Explorer, search, crests, and team themes
-   [x] Team analytics routing and dashboard
-   [x] Predictor interface and result visualization
-   [x] Prediction History UI
-   [x] Clear History button and in-app confirmation modal
-   [x] Loading, error, and empty states
-   [x] Responsive desktop/tablet/mobile layouts

### Analytics and interactions

-   [x] League analytics and KPI cards
-   [x] Season outcome and goals trends
-   [x] Historical team performance table and rankings
-   [x] Responsive chart sizing
-   [x] Motion page transitions and animated KPIs
-   [x] Team-card, button, and sidebar interactions
-   [x] Reduced-motion handling
-   [ ] Advanced chart interactions
-   [ ] Additional animation refinement

### Final polish and QA

-   [ ] Full end-to-end QA
-   [ ] Cross-page interaction verification
-   [ ] Final responsive regression check
-   [ ] Performance optimization
-   [ ] Final UI/UX refinement
-   [ ] Final GitHub repository cleanup
-   [ ] Final README review

## Future improvements

-   Improve draw prediction
-   Calibrate predicted probabilities
-   Add football-specific features
-   Make rest-day calculations fixture-date-aware
-   Integrate live/current-season data
-   Expand team-specific statistical APIs
-   Add advanced team comparisons and interactive profiles
-   Analyse model confidence
-   Track prediction performance and historical accuracy
-   Add further visual analytics and performance optimization

Model optimization will be revisited after the current application
experience and remaining product work are complete.

## Project philosophy

### Data over decoration

Numerical information should be visualized when a chart improves
comprehension.

### No fake statistics

Displayed analytical values should originate from the underlying dataset
or backend services.

### Modular architecture

Machine learning, backend services, database operations, and frontend
components are separated for maintainability.

### Real-world evaluation

Models are evaluated chronologically to better represent future
prediction scenarios.

### UX matters

The goal is an interactive football analytics platform rather than
simply an ML model exposed through an API.

### Controlled animation

Animation should improve usability, feedback, and perceived
responsiveness.

## Project status

The core machine-learning, backend, database, dashboard, analytics,
prediction, history, responsive-design, branding, and animation systems
are implemented. The project is in the **final refinement and QA
stage**, with remaining work focused on verification, cleanup, and
additional polish.
