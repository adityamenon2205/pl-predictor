# ⚽ Premier League Match Predictor

A full-stack football analytics platform that combines a machine learning prediction pipeline with a React dashboard, backed by MongoDB Atlas and a FastAPI backend.

The system predicts Premier League match outcomes as:

- 🏠 **Home Win**
- 🤝 **Draw**
- ✈️ **Away Win**

It combines historical Premier League match data with engineered team-performance features, Elo ratings, home/away statistics, form, rest days, and betting-market information to generate probability-based predictions.

> **Current status:** Machine learning pipeline and FastAPI backend completed. MongoDB Atlas integration implemented. The React frontend is under active development.

---

## 📌 Overview

The Premier League Match Predictor is designed to estimate the outcome of a Premier League fixture using historical data and machine learning.

The current production baseline is **Random Forest V4**, trained using a chronological train/test split. This approach simulates real-world prediction by ensuring future matches are not used to train the model before evaluation.

The application consists of:

- 🐍 Python machine learning pipeline
- ⚡ FastAPI backend
- 🍃 MongoDB Atlas database
- ⚛️ React frontend

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

Model experimentation and optimization will continue after the complete application is operational.

---

## 📈 Evaluation Methodology

The model is evaluated using a **chronological train/test split** rather than a random split.

### Training Data

Premier League seasons:

`2010/11 → 2024/25`

### Test Data

**2025/26**

The test set contains **380 matches**.

### Excluded Data

The **2026/27 season is excluded from model training and evaluation** because it is incomplete.

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
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         Prediction      Teams      Statistics
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                      MongoDB Atlas
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
                Match Data   Prediction History
                    │             │
                    └──────┬──────┘
                           │
                           ▼
                      React Frontend
                           │
                           ▼
                    Analytics Dashboard
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
| GET | `/statistics/` | Retrieve league statistics |
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

**Database:** `pl_predictor`

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

The prediction history endpoint retrieves these records for display in the frontend.

---

## ⚛️ Frontend

The frontend is being developed using:

- React
- Vite
- JavaScript
- React Router
- Recharts
- CSS

The frontend communicates with the FastAPI backend through REST API requests.

### Current Frontend Architecture

```text
frontend/
└── src/
    ├── assets/
    ├── components/
    │   ├── cards/
    │   ├── charts/
    │   ├── common/
    │   └── layout/
    ├── pages/
    │   ├── Overview.jsx
    │   ├── Teams.jsx
    │   ├── Predictor.jsx
    │   ├── Analytics.jsx
    │   └── History.jsx
    ├── services/
    │   └── api.js
    ├── App.css
    ├── App.jsx
    ├── index.css
    └── main.jsx
```

---

## 📊 Dashboard

The frontend is being developed as a full football analytics dashboard rather than a simple prediction form.

### 🏠 Overview

Provides a high-level statistical snapshot of the Premier League dataset.

Currently implemented:

- Total matches
- Home win percentage
- Draw percentage
- Away win percentage
- Number of teams
- Match outcome distribution
- League dataset snapshot

The Overview page retrieves real data from `GET /statistics/` and `GET /teams/`, and visualizes match outcomes using an interactive Recharts visualization.

> **No artificial or manually generated statistics are used in the dashboard.**

### ⚽ Teams

Planned functionality:

- Team cards
- Team statistics
- Team performance metrics
- Home/away performance
- Form
- Goals scored and conceded
- Team comparisons

Team-specific visual styling will also be used:

| Team | Colors |
|---|---|
| Arsenal | Red / White |
| Chelsea | Blue / White |
| Liverpool | Red |
| Manchester City | Sky Blue |

The application's main interface will retain the project's purple visual identity while individual team components use their respective club-inspired color schemes.

### 🔮 Predictor

The main machine learning interface. Users will be able to:

- Select a home team
- Select an away team
- Submit the match
- Receive the predicted outcome
- View the probability distribution

Example:

```text
Arsenal  vs  Chelsea

         HOME WIN
           41.07%

Home Win      Draw      Away Win
41.07%       35.18%      23.75%
```

The predictor communicates directly with `POST /predict/`.

### 📈 Analytics

Provides deeper exploration of historical Premier League data.

Planned visualizations include:

- Season-by-season outcome trends
- Goals per season
- Home vs away performance
- Team performance comparisons
- Win-rate comparisons
- PPG comparisons
- Goal statistics
- Other historical performance metrics

Where numerical information can be understood more effectively through visualization, charts and graphs will be preferred over raw numerical values.

### 🕐 Prediction History

Displays predictions previously generated through the application.

Predictions are retrieved from `GET /predictions/` and stored in MongoDB Atlas. The interface will allow users to browse previous predictions in a structured dashboard format rather than raw JSON.

---

## 🎨 UI / UX Design

The application uses a dark visual design centered around the primary brand color **`#541E5D`**.

The interface uses:

- Deep purple backgrounds
- Purple gradients
- White and off-white typography
- Dark translucent surfaces
- Rounded cards
- Subtle borders
- Data visualizations
- Responsive layouts

The design goal is to create a modern football analytics platform while maintaining clear visual hierarchy and readability.

Team-specific sections will use club-inspired color palettes while the overall application branding remains based around the primary purple theme.

---

## ✨ Animation & Interaction

Animations are intentionally treated as a final polish layer rather than a core development dependency.

After the major functionality and UI are complete, the project may incorporate:

- React Motion animations
- React Bits components
- Page transitions
- Animated statistics
- Hover interactions
- Scroll-based reveals
- Prediction result animations
- Micro-interactions
- Interactive chart transitions

The goal is to use animation to improve usability and visual feedback rather than adding effects purely for decoration.

---

## 📁 Project Structure

```text
pl-predictor/
│
├── backend/
│   ├── .env
│   ├── requirements.txt
│   │
│   └── app/
│       ├── main.py
│       │
│       ├── api/
│       │   ├── prediction.py
│       │   ├── predictions.py
│       │   ├── statistics.py
│       │   └── teams.py
│       │
│       ├── database/
│       │   ├── db_collections.py
│       │   ├── mongodb.py
│       │   └── seed.py
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
│           └── statistics_service.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── cards/
│   │   │   ├── charts/
│   │   │   ├── common/
│   │   │   └── layout/
│   │   │
│   │   ├── pages/
│   │   │   ├── Overview.jsx
│   │   │   ├── Teams.jsx
│   │   │   ├── Predictor.jsx
│   │   │   ├── Analytics.jsx
│   │   │   └── History.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
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
│   │
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   │
│   ├── models/
│   │   ├── random_forest_model.pkl
│   │   ├── random_forest_v4.pkl
│   │   ├── xgboost_model.pkl
│   │   └── ...
│   │
│   ├── notebooks/
│   │   └── exploration.ipynb
│   │
│   ├── preprocessing/
│   │   ├── clean_data.py
│   │   ├── feature_engineering.py
│   │   ├── feature_engineering_v2.py
│   │   └── feature_engineering_v3.py
│   │
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

---

## 🛠️ Technology Stack

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
- CSS

### Development

- Git
- GitHub
- Jupyter Notebook
- VS Code

---

## 🚀 Running the Project

### 1. Start the Backend

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

`http://127.0.0.1:8000`

FastAPI Swagger documentation:

`http://127.0.0.1:8000/docs`

### 2. Start the Frontend

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

`http://localhost:5173`

---

## 🗄️ Database Setup

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

---

## 🔐 Environment Variables

The following environment variables are required by the backend:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=pl_predictor
```

> **Security:** Sensitive credentials and environment files should never be committed to GitHub.

---

## 🔄 Application Data Flow

### Prediction Workflow

```text
User selects teams
       │
       ▼
React Frontend
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

### Prediction History Flow

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

---

## 📌 Current Development Status

### Machine Learning

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

### Backend

- [x] FastAPI application
- [x] Prediction API
- [x] Teams API
- [x] Statistics API
- [x] Prediction history API
- [x] Prediction service
- [x] Feature service
- [x] Shared service architecture
- [x] CORS configuration

### Database

- [x] MongoDB Atlas cluster
- [x] MongoDB connection
- [x] Matches collection
- [x] Teams collection
- [x] Predictions collection
- [x] Database seeding
- [x] Prediction persistence
- [x] Prediction history retrieval

### Frontend

- [x] React + Vite setup
- [x] ESLint
- [x] React Router
- [x] Application layout
- [x] Sidebar navigation
- [x] Page structure
- [x] API service layer
- [x] FastAPI integration
- [x] Overview dashboard
- [x] Real statistics from backend
- [x] Recharts integration
- [x] Initial responsive styling

### In Progress

- [ ] Complete Teams Explorer
- [ ] Team-specific statistics
- [ ] Team color themes
- [ ] Team detail pages
- [ ] Complete Predictor interface
- [ ] Advanced Analytics page
- [ ] Season-level analytics APIs
- [ ] Prediction History UI
- [ ] Advanced data visualizations
- [ ] Responsive/mobile refinement

### Final Polish

- [ ] Motion animations
- [ ] React Bits components
- [ ] Page transitions
- [ ] Micro-interactions
- [ ] Loading states
- [ ] Error states
- [ ] Empty states
- [ ] Performance optimization
- [ ] Final UI/UX refinement

---

## 🎯 Future Improvements

Potential future improvements include:

- More advanced ensemble models
- Improved draw prediction
- Probability calibration
- Additional football-specific features
- Fixture-date-aware rest calculations
- Live/current-season data integration
- Team-specific statistical APIs
- Advanced team comparison
- Model confidence analysis
- Prediction performance tracking
- Historical prediction accuracy
- More advanced visual analytics
- Interactive team profiles
- Responsive mobile dashboard
- Animated UI interactions

Model optimization will be revisited after the full application is operational.

---

## 📜 Project Philosophy

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
