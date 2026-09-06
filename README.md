# ⚽ Premier League Match Predictor

An end-to-end machine learning application for predicting English Premier League match outcomes using historical match data, team performance, form, Elo ratings, home/away statistics, rest days, and betting-market information.

> **Current status:** Machine learning pipeline completed. FastAPI backend and core APIs implemented. MongoDB and React dashboard are the next development stages.

---

## 📌 Overview

The Premier League Match Predictor is a machine learning application designed to estimate the outcome of a Premier League fixture as:

- 🏠 **Home Win**
- 🤝 **Draw**
- ✈️ **Away Win**

The system uses historical Premier League match data to generate team-performance features and predict match outcomes using machine learning.

The current production baseline is a **Random Forest classifier** trained using a chronological train/test split. This approach simulates real-world prediction by ensuring that future matches are not used to train the model before evaluating it.

The application is being developed as a full-stack system consisting of:

- 🐍 Python machine learning pipeline
- ⚡ FastAPI backend
- ⚛️ React frontend
- 🍃 MongoDB database

---

## 🧠 Machine Learning

### Feature Engineering

The feature engineering pipeline incorporates:

- Recent form over the previous 3, 5, and 10 matches
- Points per game (PPG)
- Win rates
- Goals scored and conceded
- Goal difference
- Shots and shots on target
- Corners
- Home-team and away-team performance splits
- Elo ratings
- Rest days between matches
- Relative team-strength features
- Betting-market implied probabilities
- Market margins
- Team balance/difference features

All rolling and historical features are generated using information available **before the current match**, helping prevent future information leakage.

The final V4 feature set contains **100 model features**.

---

## 🤖 Model Development

Several approaches were evaluated during development:

| Model | Accuracy | Macro F1 | Draw F1 |
|---|---:|---:|---:|
| **Random Forest V4** | **50.00%** | 0.3792 | 0.0189 |
| Balanced XGBoost V4 | 43.68% | **0.3819** | **0.1410 |
| Poisson V5 | 48.68% | 0.3621 | 0.0000 |

The **Random Forest V4 model** is currently the production baseline because it achieved the highest overall accuracy on the held-out 2025/26 season.

Model experimentation and optimization will continue after the first complete application is operational.

---

## 📊 Evaluation Methodology

The model is evaluated using a chronological train/test split rather than a random split.

### Training Data

**Premier League seasons:**

`2010/11 → 2024/25`

### Test Data

**2025/26**

The test set contains:

**380 matches**

### Excluded Data

The **2026/27 season is excluded from model training and evaluation** because it is incomplete.

This chronological approach better represents a real-world prediction scenario and reduces the risk of future information leaking into the training process.

---

## 📈 Current Model Performance

The Random Forest V4 model achieved the following results on the held-out 2025/26 season:

| Metric | Result |
|---|---:|
| Accuracy | **50.00%** |
| Log Loss | 1.0315 |
| Macro F1 | 0.3792 |
| Draw F1 | 0.0189 |
| Test Matches | 380 |

The model currently performs considerably better at identifying home wins than draws. Draw prediction remains an area for future model improvement.

---

## 🗂️ Data

Historical Premier League match data is sourced from:

**Football-Data.co.uk**

The raw datasets contain match results and additional match statistics, including:

- Goals
- Shots
- Shots on target
- Corners
- Bookmaker odds
- Match results

The preprocessing pipeline cleans and combines the historical season data before generating the features used by the machine learning models.

---

## 🏗️ Backend

The application currently uses **FastAPI** to expose the machine learning functionality through REST APIs.

### Current API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| GET | `/teams/` | Retrieve available Premier League teams |
| GET | `/statistics/` | Retrieve historical league statistics |
| POST | `/predict/` | Predict the outcome of a fixture |

### Example Prediction Request

```json
{
  "home_team": "Arsenal",
  "away_team": "Chelsea"
}
