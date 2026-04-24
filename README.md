# Crash AI API - Signé SOLITAIRE HACK 🇨🇮

IA statistique d'aide à l'analyse du jeu Crash.

## ⚠️ Avertissement Important

Ce projet est une IA statistique d'aide à l'analyse uniquement. Il ne doit jamais promettre une prédiction garantie ou un gain certain. Les jeux de hasard comportent des risques importants.

## 📁 Structure du Projet

```
crash-ai-api/
├── main.py
├── TRAIN-666.CSV
├── crash_ai_model.joblib (généré après entraînement)
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Démarrage Local

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 Endpoints API

### GET `/`

Statut de l'API.

**Réponse:**
```json
{
  "status": "Crash AI API running",
  "project": "SOLITAIRE HACK 🇨🇮"
}
```

### POST `/train`

Entraîne le modèle sur les données du CSV.

**Réponse:**
```json
{
  "status": "training_completed",
  "rows_used": 1200,
  "model_file": "crash_ai_model.joblib",
  "accuracy": 0.74
}
```

### POST `/predict`

Fait une prédiction basée sur les features fournies.

**Corps de la requête:**
```json
{
  "hour": 4,
  "minute": 49,
  "second": 12,
  "prev_1": 5.33,
  "prev_2": 1.42,
  "prev_3": 2.31,
  "avg_5": 2.13,
  "low_count_5": 2,
  "high_count_10": 1
}
```

**Réponse:**
```json
{
  "prediction": 1,
  "confidence": 0.85,
  "signal": "ENTRÉE PRUDENTE"
}
```

**Erreur si modèle non entraîné:**
```json
{
  "error": "Model not trained yet. Call /train first."
}
```

## 🧠 Features Utilisées

- **hour**: Heure du timestamp
- **minute**: Minute du timestamp
- **second**: Seconde du timestamp
- **prev_1**: Valeur du round précédent
- **prev_2**: Valeur 2 rounds avant
- **prev_3**: Valeur 3 rounds avant
- **avg_5**: Moyenne des 5 derniers rounds
- **low_count_5**: Nombre de valeurs < 2.0 dans les 5 derniers rounds
- **high_count_10**: Nombre de valeurs >= 2.0 dans les 10 derniers rounds

## 🎯 Cible (Target)

- **1**: Si value >= 2.0
- **0**: Si value < 2.0

## 🌐 Configuration Render

**Build command:**
```
pip install -r requirements.txt
```

**Start command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## 📦 Dépendances

- fastapi
- uvicorn
- pandas
- numpy
- scikit-learn
- joblib
- pydantic

---

**Signé:** SOLITAIRE HACK 🇨🇮
