# ⚽ Premier League Match Predictor

A full-stack football analytics platform that combines a machine learning prediction pipeline with a React dashboard, backed by MongoDB Atlas and a FastAPI backend.

The system predicts Premier League match outcomes as:

- 🏠 **Home Win**
- 🤝 **Draw**
- ✈️ **Away Win**

It combines historical Premier League match data with engineered team-performance features, Elo ratings, home/away statistics, form, rest days, and betting-market information to generate probability-based predictions.

> **Current status:** The machine learning pipeline, FastAPI backend, MongoDB Atlas integration, Overview dashboard, Teams Explorer, team-specific Analytics, Predictor interface, Prediction History, League Analytics, responsive layouts, branded UI, page transitions, animated KPI values, and micro-interactions are implemented. Current work is focused on final QA, remaining UI refinement, and project cleanup/documentation.

---

## 📌 Overview

The Premier League Match Predictor estimates the outcome of a Premier League fixture using historical data and machine learning.

The current production baseline is **Random Forest V4**, trained using a chronological train/test split. This approach simulates real-world prediction by ensuring future matches are not used to train the model before evaluation.

The application consists of:

- 🐍 Python machine learning pipeline
- ⚡ FastAPI backend
- 🍃 MongoDB Atlas database
- ⚛️ React + Vite frontend
- 📊 Recharts-based analytics dashboard
- 🎞️ Motion-based UI animations and transitions
- 🎨 Club-inspired visual themes and custom product branding

---

## 📊 Current Model Performance

The **Random Forest V4** model achieved the following results on the held-out **2025/26 season**:

| Metric | Result |
|---|---:|
| Accuracy | **50.00%** |
| Log Loss | 1.0315 |
| Macro F1 | 0.3792 |
| Draw F1 | 0.0189 |
| Test Matches | 380 |

The model currently performs considerably better at identifying home wins than draws. Draw prediction remains an important area for future model improvement.

### Model Comparison

Several approaches were evaluated during development:

| Model | Accuracy | Macro F1 | Draw F1 |
|---|---:|---:|---:|
| **Random Forest V4** | **50.00%** | 0.3792 | 0.0189 |
| Balanced XGBoost V4 | 43.68% | **0.3819** | **0.1410** |
| Poisson V5 | 48.68% | 0.3621 | 0.0000 |

**Random Forest V4** is currently used as the production baseline because it achieved the highest overall accuracy on the held-out 2025/26 season.

Model experimentation is currently paused while the application experience, analytics, and frontend are completed.

---

## 📈 Evaluation Methodology

The model is evaluated using a **chronological train/test split** rather than a random split.

### Training Data

Premier League seasons:

```text
2010/11 → 2024/25
```

### Test Data

```text
2025/26
```

The test set contains **380 matches**.

### Excluded Data

The **2026/27 season is excluded from model training and evaluation** because the available season data is incomplete.

This chronological approach better represents a real-world prediction scenario and reduces the risk of future information leaking into the training process.

---

## 🧠 Machine Learning

### Feature Engineering

The feature engineering pipeline incorporates:

- Recent form over the previous 3, 5, and 10 matches
- Points per game (PPG)
- Win rates
- Goals scored and conceded
- Goal difference
- Shots
- Shots on target
- Corners
- Fouls
- Yellow cards
- Red cards
- Home-team and away-team performance splits
- Elo ratings
- Rest days
- Relative team-strength features
- Betting-market implied probabilities
- Market margins
- Team balance/difference features

All rolling and historical features are generated using information available **before the current match**, helping prevent future information leakage.

The final V4 feature set contains **100 model features**.

---

## 🗂️ Data

Historical Premier League match data is sourced from **Football-Data.co.uk**.

The raw datasets contain match results and additional match statistics, including:

- Full-time goals
- Half-time goals
- Shots
- Shots on target
- Corners
- Fouls
- Yellow cards
- Red cards
- Bookmaker odds
- Match results

The preprocessing pipeline cleans and combines the historical season data before generating the features used by the machine learning models.

### Current Processed Dataset

- **6,080 completed Premier League matches**
- **16 completed seasons**
- **2010/11 through 2025/26**

The 2025/26 season is included in the processed historical dataset but is reserved as the held-out test season for the current Random Forest V4 evaluation.

The incomplete 2026/27 season is excluded from training and evaluation.

---

## 🏗️ Application Architecture

The application follows a modular architecture separating the machine learning pipeline, backend services, database layer, and frontend.

```text
                         Historical EPL Data
                                  │
                                  ▼
                         Data Preprocessing
                                  │
                                  ▼
                         Feature Engineering
                                  │
                                  ▼
                           Model Training
                                  │
                                  ▼
                          Random Forest V4
                                  │
                                  ▼
                               FastAPI
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
                Prediction      Teams       Statistics
                    │             │             │
                    └─────────────┼─────────────┘
                                  │
                                  ▼
                            MongoDB Atlas
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
                Match Data               Prediction History
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                            React Frontend
                                  │
                                  ▼
                       Football Analytics Dashboard
```

---

## ⚡ Backend

The backend is implemented using **FastAPI**, providing REST API endpoints for predictions, team information, statistics, and prediction history.

### Backend API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/teams/` | Retrieve available teams |
| GET | `/teams/{team_name}/statistics` | Retrieve historical statistics for a specific team |
| GET | `/statistics/` | Retrieve league analytics/statistics |
| POST | `/predict/` | Generate a match prediction |
| GET | `/predictions/` | Retrieve prediction history |

### Example Prediction Request

```json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea"
}
```

### Example Prediction Response

```json
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

The prediction service loads the trained Random Forest V4 model, generates the required 100 features through the feature service, performs the prediction, and stores the result in MongoDB.

---

## 🍃 MongoDB Atlas

MongoDB Atlas is used as the application's database layer.

**Database:**

```text
pl_predictor
```

### Collections

#### `matches`

Stores the historical Premier League match dataset.

- Current records: **6,080 matches**

#### `teams`

Stores the unique teams present in the historical dataset.

- Current records: **41 teams**

#### `predictions`

Stores predictions generated through the `/predict/` API.

Each prediction contains:

- Home team
- Away team
- Predicted outcome
- Home probability
- Draw probability
- Away probability
- Prediction timestamp

The prediction history endpoint retrieves these records for display in the frontend.

---

# ⚛️ Frontend

The frontend is implemented using:

- React
- Vite
- JavaScript
- React Router
- Recharts
- Motion
- CSS

The frontend communicates with the FastAPI backend through REST API requests. API calls are centralized in `src/services/api.js`.

### Current Frontend Architecture

```text
frontend/
├── public/
│   ├── pl_predictor_logo.svg
│   ├── pl_predictor_logo.png
│   └── pl_predictor_favicon.png
│
└── src/
    ├── assets/
    │
    ├── components/
    │   ├── cards/
    │   ├── charts/
    │   ├── common/
    │   │   ├── AnimatedNumber.jsx
    │   │   └── PageTransition.jsx
    │   └── layout/
    │
    ├── data/
    │   └── teams.js
    │
    ├── pages/
    │   ├── Overview.jsx
    │   ├── Teams.jsx
    │   ├── Predictor.jsx
    │   ├── Analytics.jsx
    │   └── History.jsx
    │
    ├── services/
    │   └── api.js
    │
    ├── App.css
    ├── App.jsx
    ├── index.css
    └── main.jsx
```

---

# 📊 Dashboard

The frontend is developed as a full football analytics dashboard rather than a simple prediction form.

## 🏠 Overview

Provides a high-level statistical snapshot of the Premier League dataset.

Implemented:

- Total matches
- Home win percentage
- Draw percentage
- Away win percentage
- Number of teams
- Match outcome distribution
- League dataset snapshot
- Animated KPI values
- Recharts outcome visualization
- Page entrance transition

The Overview page retrieves real data from the backend and visualizes match outcomes using Recharts.

> **No artificial or manually generated statistics are used in the dashboard.**

---

## ⚽ Teams Explorer

The Teams Explorer retrieves available clubs from the backend and presents them as team-specific cards.

Implemented:

- Team cards for the historical dataset's **41 teams**
- Searchable Teams Explorer
- Club-inspired primary, secondary, and accent color themes
- Team crests
- Hover interactions
- Team-card motion effects
- Navigation from a team card to its Analytics view
- Real team statistics retrieved from `/teams/{team_name}/statistics`

### Team Analytics

Current team analytics include:

- Matches played
- Wins, draws, and losses
- Win/draw/loss percentages
- Goals scored and conceded
- Goal difference
- Home record
- Away record
- Result distribution chart
- Goals scored vs conceded chart
- Home vs away performance chart
- Historical highlight
- Animated KPI values
- Team-specific visual styling

Team-specific visual styling is used throughout the Teams Explorer, Analytics dashboard, and prediction results.

| Team | Example colors |
|---|---|
| Arsenal | Red / White |
| Chelsea | Blue / White |
| Liverpool | Red |
| Manchester City | Sky Blue |

The application's main interface retains the project's purple visual identity while individual team components use their respective club-inspired color schemes.

---

## 🔮 Predictor

The Predictor is the main machine learning interface.

Users can:

- Search for a home team
- Search for an away team
- Select teams using crest-enhanced selectors
- Submit a fixture for prediction
- Receive the predicted outcome
- View home/draw/away probability percentages
- View the prediction result using team-specific visual styling
- See animated prediction/probability presentation

Example:

```text
Arsenal  vs  Chelsea

        HOME WIN
          41.07%

Home Win       Draw       Away Win
41.07%         35.18%       23.75%
```

The predictor communicates directly with:

```text
POST /predict/
```

Predictions are also persisted to MongoDB Atlas for the History page.

---

# 📈 Analytics

The Analytics section contains both **team-specific analytics** and **league-wide historical analytics**.

## Team Analytics

When a team is selected from the Teams Explorer, the Analytics page provides:

- Team identity and crest
- Team-specific club-inspired color theme
- Matches, wins, draws, and losses KPI cards
- Win/draw/loss percentages
- Match-result distribution donut chart
- Goals scored vs conceded chart
- Goal-difference summary
- Home vs away performance chart
- Real statistics retrieved through the FastAPI backend
- Animated KPI values
- Page transitions

## League Analytics

The default Analytics route provides league-wide historical analysis.

Implemented:

- Total matches KPI
- Total goals KPI
- Goals per match KPI
- Home win rate KPI
- Season-by-season match outcome trends
- Home win percentage trends
- Draw percentage trends
- Away win percentage trends
- Goals-per-match trends
- Home vs away goals-per-match comparison
- Historical team performance table
- Team rankings
- Matches, wins, draws, losses, goal difference, points, and win percentage
- Animated KPI values
- Responsive chart rendering
- Mobile-friendly chart sizing

The league analytics use real historical data rather than manually created readings.

### Responsive Analytics

The Analytics dashboard includes responsive handling for narrow viewports, including:

- Reliable chart sizing
- Mobile chart rendering
- Responsive dashboard layout
- Prevention of horizontal overflow
- Readable chart labels on smaller screens

Where numerical information can be understood more effectively through visualization, charts and graphs are preferred over raw numerical values.

---

# 🕐 Prediction History

The Prediction History page is implemented.

It retrieves prediction records through:

```text
GET /predictions/
```

and displays them in a structured dashboard interface.

Implemented:

- Prediction count
- Historical prediction cards
- Home and away teams
- Team crests
- Predicted outcome
- Home/draw/away probabilities
- Prediction timestamps
- Outcome-specific visual styling
- Loading state
- Error state
- Empty state handling
- Responsive layout
- Hover/micro-interactions
- Page transition

Prediction history is backed by MongoDB Atlas rather than static frontend data.

---

# 🎨 UI / UX Design

The application uses a dark visual design centered around the primary brand color:

```text
#541E5D
```

The interface uses:

- Deep purple backgrounds
- Purple gradients
- White and off-white typography
- Dark translucent surfaces
- Rounded cards
- Subtle borders
- Data visualizations
- Responsive layouts
- Club-inspired team colors
- Football crests
- Custom product branding
- Motion-based transitions
- Subtle hover and interaction feedback

### Product Branding

The application now uses a custom **PL Predictor** visual identity.

The branding includes:

- Custom PL motion-style logo
- Transparent logo artwork for the sidebar
- Dedicated browser favicon
- `PL Predictor` browser-tab title
- Consistent purple/magenta visual language

The sidebar uses the full branded logo, while the browser tab uses the compact favicon version.

### Interaction Design

The project includes lightweight micro-interactions such as:

- Sidebar navigation hover movement
- Team-card lift effects
- Team crest hover motion
- Team-card arrow movement
- Card hover elevation
- Button press feedback
- Input focus transitions
- Responsive hover handling
- Reduced-motion support

The design aims to improve feedback without overwhelming the analytical content.

---

# ✨ Animation & Interaction

Animation is treated as a **final polish layer** rather than the foundation of the application.

The current implementation uses **Motion for React**.

Implemented:

- Page entrance transitions
- Animated KPI/statistic values
- Team-card hover interactions
- Sidebar navigation interactions
- Button interactions
- Card hover effects
- Prediction result animation/presentation
- Recharts animation where appropriate
- Reduced-motion accessibility handling

### Shared Animation Components

```text
src/components/common/
├── AnimatedNumber.jsx
└── PageTransition.jsx
```

`PageTransition` provides consistent page-level entrance animation across the major dashboard pages.

`AnimatedNumber` provides spring-based animated numeric values for KPI/statistical displays.

### React Bits

React Bits was evaluated as a potential source of additional UI effects and components, but it is **not currently a core dependency of the implemented interface**. Additional components may be considered during later polish if they provide a clear UX benefit.

The goal is to use animation to improve usability and visual feedback rather than adding effects purely for decoration.

---

# 📱 Responsive Design

The frontend has been refined for different viewport sizes.

Responsive work includes:

- Desktop dashboard layout
- Tablet-friendly grids
- Mobile navigation layout
- Stacked dashboard cards
- Responsive team cards
- Responsive predictor layout
- Responsive history cards
- Responsive analytics charts
- Prevention of horizontal overflow
- Mobile chart sizing
- Touch-friendly interaction behavior

The responsive layout has been tested across the main dashboard pages and refined to maintain usability at narrower viewport sizes.

---

# 📁 Project Structure

```text
pl-predictor/
│
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       │
│       ├── api/
│       │   ├── prediction.py
│       │   ├── predictions.py
│       │   ├── statistics.py
│       │   ├── teams.py
│       │   └── __init__.py
│       │
│       ├── database/
│       │   ├── db_collections.py
│       │   ├── mongodb.py
│       │   ├── seed.py
│       │   └── __init__.py
│       │
│       ├── models/
│       │   └── prediction_model.py
│       │
│       ├── schemas/
│       │   ├── prediction.py
│       │   └── teams.py
│       │
│       └── services/
│           ├── container.py
│           ├── feature_service.py
│           ├── prediction_history_service.py
│           ├── prediction_service.py
│           ├── statistics_service.py
│           └── __init__.py
│
├── frontend/
│   ├── public/
│   │   ├── pl_predictor_logo.svg
│   │   ├── pl_predictor_logo.png
│   │   └── pl_predictor_favicon.png
│   │
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── cards/
│   │   │   ├── charts/
│   │   │   ├── common/
│   │   │   │   ├── AnimatedNumber.jsx
│   │   │   │   └── PageTransition.jsx
│   │   │   └── layout/
│   │   ├── data/
│   │   │   └── teams.js
│   │   ├── pages/
│   │   │   ├── Overview.jsx
│   │   │   ├── Teams.jsx
│   │   │   ├── Predictor.jsx
│   │   │   ├── Analytics.jsx
│   │   │   └── History.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── ml/
│   ├── config.py
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── models/
│   │   ├── random_forest_model.pkl
│   │   ├── random_forest_v2.pkl
│   │   ├── random_forest_v3.pkl
│   │   ├── random_forest_v4.pkl
│   │   ├── xgboost_model.pkl
│   │   └── ...
│   ├── notebooks/
│   │   └── exploration.ipynb
│   ├── preprocessing/
│   │   ├── clean_data.py
│   │   ├── feature_engineering.py
│   │   ├── feature_engineering_v2.py
│   │   └── feature_engineering_v3.py
│   └── training/
│       ├── train_random_forest.py
│       ├── train_random_forest_v2.py
│       ├── train_random_forest_v3.py
│       ├── train_xgboost.py
│       ├── train_xgboost_v2.py
│       ├── train_xgboost_v2_balanced.py
│       ├── train_xgboost_v3.py
│       ├── train_models_v4.py
│       ├── evaluate_models.py
│       ├── create_features_v4.py
│       ├── analyze_probabilities.py
│       ├── analyze_draw_threshold.py
│       ├── calibrate_model.py
│       └── evaluate_poisson_v5.py
│
├── .gitignore
└── README.md
```

> Trained model binaries, generated processed datasets, environment files, and other generated/private files are excluded from version control according to `.gitignore`.

---

# 🛠️ Technology Stack

### Machine Learning

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Joblib

### Backend

- FastAPI
- Uvicorn
- Pydantic
- PyMongo
- Python-dotenv

### Database

- MongoDB Atlas

### Frontend

- React
- Vite
- JavaScript
- React Router
- Recharts
- Motion
- CSS

### Development

- Git
- GitHub
- Jupyter Notebook
- VS Code

---

# 🚀 Running the Project

## 1. Start the Backend

From the project root:

```bash
cd backend
```

Activate the virtual environment if required:

```bash
source ../.venv/Scripts/activate
```

Then start FastAPI:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 2. Start the Frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies if required:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

---

# 🗄️ Database Setup

The MongoDB connection is configured through environment variables.

Example:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=pl_predictor
```

> The `.env` file is intentionally excluded from version control.

To seed the historical match data into MongoDB:

```bash
cd backend
python -m app.database.seed
```

The seed process populates the `matches` and `teams` collections with the processed Premier League dataset.

Prediction records are subsequently written to the `predictions` collection when predictions are generated through the application.

---

# 🔐 Environment Variables

The backend requires:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=pl_predictor
```

> **Security:** Sensitive credentials and environment files should never be committed to GitHub.

---

# 🔄 Application Data Flow

## Prediction Workflow

```text
User selects teams
       │
       ▼
React Predictor
       │
       ▼
POST /predict/
       │
       ▼
FastAPI
       │
       ▼
Prediction Service
       │
       ▼
Feature Service
       │
       ▼
100 engineered features
       │
       ▼
Random Forest V4
       │
       ▼
Prediction + probabilities
       │
       ├──────────────► MongoDB Atlas
       │
       ▼
FastAPI Response
       │
       ▼
React Dashboard
       │
       ▼
Prediction Result
```

## Prediction History Flow

```text
Prediction
     │
     ▼
MongoDB
     │
     ▼
GET /predictions/
     │
     ▼
React History Page
```

## Analytics Flow

```text
MongoDB match data
        │
        ▼
Statistics Service
        │
        ▼
GET /statistics/
        │
        ▼
React Analytics Dashboard
        │
        ├── League Analytics
        │
        └── Team Analytics
```

---

# 📌 Current Development Status

## Machine Learning

- [x] Historical data collection
- [x] Data cleaning
- [x] Feature engineering
- [x] Rolling form features
- [x] Elo ratings
- [x] Home/away statistics
- [x] Betting-market features
- [x] Feature balance/difference metrics
- [x] Random Forest experiments
- [x] XGBoost experiments
- [x] Poisson experiment
- [x] Chronological evaluation
- [x] Random Forest V4 production baseline
- [x] 2025/26 held-out evaluation
- [x] 2026/27 exclusion from training/evaluation
- [ ] Future model optimization

## Backend

- [x] FastAPI application
- [x] Prediction API
- [x] Teams API
- [x] Statistics API
- [x] Prediction history API
- [x] Prediction service
- [x] Feature service
- [x] Prediction history service
- [x] Shared service architecture
- [x] CORS configuration
- [x] MongoDB Atlas integration

## Database

- [x] MongoDB Atlas cluster
- [x] MongoDB connection
- [x] Matches collection
- [x] Teams collection
- [x] Predictions collection
- [x] Database seeding
- [x] Prediction persistence
- [x] Prediction history retrieval

## Frontend

- [x] React + Vite setup
- [x] ESLint
- [x] React Router
- [x] Application layout
- [x] Sidebar navigation
- [x] Custom PL Predictor branding
- [x] Browser favicon and page title
- [x] Page structure
- [x] API service layer
- [x] FastAPI integration
- [x] Overview dashboard
- [x] Real statistics from backend
- [x] Recharts integration
- [x] Teams Explorer
- [x] Team search
- [x] Team crest integration
- [x] Team-specific color themes
- [x] Team analytics routing
- [x] Team analytics dashboard
- [x] Predictor interface
- [x] Prediction result visualization
- [x] Prediction History UI
- [x] Loading states
- [x] Error states
- [x] Empty states
- [x] Responsive desktop/tablet/mobile layout

## League Analytics

- [x] League analytics page
- [x] League KPI cards
- [x] Animated KPI values
- [x] Season outcome trend visualization
- [x] Goals-per-match visualization
- [x] Home vs away goals visualization
- [x] Historical team performance table
- [x] Team ranking data
- [x] Responsive chart sizing
- [x] Narrow viewport rendering
- [x] Mobile layout refinement
- [x] Horizontal overflow prevention

## Animation & Interaction

- [x] Motion integration
- [x] Shared page transitions
- [x] Animated numerical statistics
- [x] Team-card hover interactions
- [x] Sidebar navigation micro-interactions
- [x] Button interaction feedback
- [x] Card hover effects
- [x] Reduced-motion handling
- [ ] Advanced chart interactions
- [ ] Additional animation refinement

## Final Polish / QA

- [ ] Full end-to-end QA
- [ ] Cross-page interaction verification
- [ ] Final responsive regression check
- [ ] Performance optimization
- [ ] Final UI/UX refinement
- [ ] Final GitHub repository cleanup
- [ ] Final README review

---

# 🎯 Future Improvements

Potential future improvements include:

- Improved draw prediction
- Probability calibration
- Additional football-specific features
- Fixture-date-aware rest calculations
- Live/current-season data integration
- Expanded team-specific statistical APIs
- Advanced team comparison
- Model confidence analysis
- Prediction performance tracking
- Historical prediction accuracy
- More advanced visual analytics
- Interactive team profiles
- Animated UI interactions
- Further performance optimization

Model optimization will be revisited after the current application experience and remaining product work are complete.

---

# 📜 Project Philosophy

The project is being developed with several principles in mind.

### Data over Decoration

Numerical information should be visualized when a chart or graph improves comprehension.

### No Fake Statistics

All displayed analytical values should originate from the underlying dataset or backend services.

### Modular Architecture

Machine learning, backend services, database operations, and frontend components are kept separated to make the application easier to maintain and extend.

### Real-World Evaluation

Models are evaluated chronologically to better represent future prediction scenarios.

### UX Matters

The final application is intended to be an interactive football analytics platform rather than simply an ML model exposed through an API.

### Controlled Animation

Animation should improve usability, feedback, and perceived responsiveness rather than exist purely as decoration.

---

## 🔒 Project Status

The core machine learning, backend, database, dashboard, analytics, prediction, history, responsive design, branding, and animation systems are implemented.

The project is now in the **final refinement and QA stage**, with remaining work focused on verification, cleanup, and a small amount of additional polish.
