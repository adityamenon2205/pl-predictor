# ⚽ Premier League Match Predictor

An end-to-end machine learning application for predicting English Premier League match outcomes using historical match data, team performance, form, Elo ratings, home/away statistics, rest days, and betting-market information.

> **Current status:** Machine learning pipeline completed. Application/API development in progress.

---

## 📌 Overview

The Premier League Match Predictor is a machine learning project designed to estimate the outcome of an upcoming Premier League fixture as:

- 🏠 **Home Win**
- 🤝 **Draw**
- ✈️ **Away Win**

The project combines historical Premier League match data with engineered team-performance features and machine learning models. The current production candidate is a **Random Forest classifier** trained using a chronological train/test split to avoid using future matches when evaluating historical predictions.

The long-term goal is to provide these predictions through a web-based dashboard with a Python backend, React frontend, and MongoDB database.

---

## 🧠 Machine Learning

### Feature Engineering

The current feature pipeline incorporates:

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

All rolling features are generated using **past matches only**, preventing future information from leaking into the training data.

### Model Development

Several approaches were evaluated during development:

| Model | Accuracy | Macro F1 | Draw F1 |
|---|---:|---:|---:|
| Random Forest V4 | **50.00%** | 0.3792 | 0.0189 |
| Balanced XGBoost V4 | 43.68% | **0.3819** | **0.1410** |
| Poisson V5 | 48.68% | 0.3621 | 0.0000 |

The **Random Forest V4 model** is currently used as the production baseline because it achieved the highest overall accuracy on the held-out 2025/26 season.

Model development and experimentation will continue after the first working application is completed.

---

## 📊 Evaluation Methodology

To simulate real-world prediction, the dataset is split chronologically rather than randomly.

### Training Data

Premier League seasons:

**2010/11 → 2024/25**

### Test Data

**2025/26**

The test set contains:

**380 matches**

The **2026/27 season is excluded from model training** because it is incomplete.

This chronological evaluation helps prevent information from future seasons leaking into the training process.

---

## 🗂️ Data

Historical Premier League match data is sourced from:

**Football-Data.co.uk**

The dataset contains match results and additional match statistics, including goals, shots, corners, and bookmaker odds.

The preprocessing pipeline converts the raw match data into a feature dataset suitable for machine learning.

---

## 🏗️ Project Architecture

The planned application architecture is:

```text
                    Premier League Data
                            │
                            ▼
                   Feature Engineering
                            │
                            ▼
                    Machine Learning
                       Model Pipeline
                            │
                            ▼
                       Random Forest
                            │
                            ▼
                         FastAPI
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
          Prediction API          Statistics API
                │                       │
                └───────────┬───────────┘
                            ▼
                       React Frontend
                            │
                            ▼
                         Dashboard
                            │
                            ▼
                         MongoDB
