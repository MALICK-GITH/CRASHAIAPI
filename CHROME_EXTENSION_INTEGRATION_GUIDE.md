# 📘 Guide d'Intégration - Extension Chrome ↔ Crash AI API

**Projet:** Crash AI API - Signé SOLITAIRE HACK 🇨🇮  
**URL API:** https://crashaiapi.onrender.com

---

## 📋 Table des matières

1. [Configuration de base](#configuration-de-base)
2. [Architecture de l'extension](#architecture-de-lextension)
3. [Endpoints disponibles](#endpoints-disponibles)
4. [Exemples de code](#exemples-de-code)
5. [Gestion des erreurs](#gestion-des-erreurs)
6. [Sécurité](#sécurité)
7. [Performance](#performance)
8. [Tests](#tests)

---

## 🔧 Configuration de base

### Manifest.json (Chrome Extension)

```json
{
  "manifest_version": 3,
  "name": "Crash AI Assistant",
  "version": "1.0.0",
  "description": "Assistant IA pour le jeu Crash - Signé SOLITAIRE HACK",
  "permissions": [
    "activeTab",
    "storage",
    "scripting"
  ],
  "host_permissions": [
    "https://crashaiapi.onrender.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ],
  "action": {
    "default_popup": "popup.html"
  }
}
```

**Points importants:**
- `host_permissions`: Autorise les requêtes vers l'API
- `manifest_version`: 3 (dernière version)
- `service_worker`: Pour les appels API en arrière-plan

---

## 🏗️ Architecture de l'extension

### Structure des fichiers

```
extension/
├── manifest.json
├── background.js       # Service worker pour appels API
├── content.js          # Injection dans la page du jeu
├── popup.html          # Interface popup
├── popup.js            # Logique popup
└── utils/
    ├── api.js          # Fonctions API
    └── features.js     # Calcul des features
```

---

## 📡 Endpoints disponibles

### 1. GET / - Vérification du statut

**URL:** `https://crashaiapi.onrender.com/`

**Méthode:** GET

**Réponse:**
```json
{
  "status": "Crash AI API running",
  "project": "SOLITAIRE HACK 🇨🇮"
}
```

**Utilisation:** Vérifier si l'API est en ligne avant les prédictions.

---

### 2. POST /predict - Prédiction principale

**URL:** `https://crashaiapi.onrender.com/predict`

**Méthode:** POST

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
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

**Signaux:**
- `ENTRÉE PRUDENTE`: Prediction = 1, confidence >= 0.7
- `ENTRÉE TRÈS PRUDENTE`: Prediction = 1, confidence < 0.7
- `ATTENDRE`: Prediction = 0

---

### 3. GET /documentation - Documentation

**URL:** `https://crashaiapi.onrender.com/documentation`

**Méthode:** GET

**Utilisation:** Afficher la documentation HTML.

---

## 💻 Exemples de code

### utils/api.js - Module API

```javascript
const API_BASE_URL = "https://crashaiapi.onrender.com";

/**
 * Vérifier si l'API est en ligne
 */
async function checkApiStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/`);
    const data = await response.json();
    return data.status === "Crash AI API running";
  } catch (error) {
    console.error("API status check failed:", error);
    return false;
  }
}

/**
 * Faire une prédiction
 * @param {Object} features - Features calculées
 * @returns {Object} - Prédiction avec confidence et signal
 */
async function makePrediction(features) {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(features),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Prediction failed:", error);
    throw error;
  }
}

/**
 * Obtenir la documentation
 */
async function getDocumentation() {
  try {
    const response = await fetch(`${API_BASE_URL}/documentation`);
    return await response.text();
  } catch (error) {
    console.error("Documentation fetch failed:", error);
    return null;
  }
}

// Export des fonctions
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { checkApiStatus, makePrediction, getDocumentation };
}
```

---

### utils/features.js - Calcul des features

```javascript
/**
 * Extraire les features temporelles
 * @param {Date} date - Date actuelle
 * @returns {Object} - hour, minute, second
 */
function extractTimeFeatures(date = new Date()) {
  return {
    hour: date.getHours(),
    minute: date.getMinutes(),
    second: date.getSeconds(),
  };
}

/**
 * Calculer les features de lag et statistiques
 * @param {Array} crashHistory - Historique des crashes [5.33, 1.42, 2.31, ...]
 * @returns {Object} - prev_1, prev_2, prev_3, avg_5, low_count_5, high_count_10
 */
function calculateFeatures(crashHistory) {
  if (!crashHistory || crashHistory.length < 3) {
    throw new Error("Need at least 3 crash values");
  }

  // Features de lag
  const prev_1 = crashHistory[0];
  const prev_2 = crashHistory[1];
  const prev_3 = crashHistory[2];

  // Moyenne des 5 derniers
  const last5 = crashHistory.slice(0, 5);
  const avg_5 = last5.reduce((a, b) => a + b, 0) / last5.length;

  // Compter les valeurs basses (< 2.0) dans les 5 derniers
  const low_count_5 = last5.filter(v => v < 2.0).length;

  // Compter les valeurs hautes (>= 2.0) dans les 10 derniers
  const last10 = crashHistory.slice(0, 10);
  const high_count_10 = last10.filter(v => v >= 2.0).length;

  return {
    prev_1,
    prev_2,
    prev_3,
    avg_5,
    low_count_5,
    high_count_10,
  };
}

/**
 * Préparer toutes les features pour l'API
 * @param {Array} crashHistory - Historique des crashes
 * @returns {Object} - Features complètes
 */
function prepareFeatures(crashHistory) {
  const timeFeatures = extractTimeFeatures();
  const crashFeatures = calculateFeatures(crashHistory);

  return {
    ...timeFeatures,
    ...crashFeatures,
  };
}

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { extractTimeFeatures, calculateFeatures, prepareFeatures };
}
```

---

### background.js - Service Worker

```javascript
import { checkApiStatus, makePrediction } from "./utils/api.js";
import { prepareFeatures } from "./utils/features.js";

// Vérifier le statut de l'API au démarrage
chrome.runtime.onStartup.addListener(async () => {
  const isOnline = await checkApiStatus();
  console.log("API Status:", isOnline ? "Online" : "Offline");
  
  // Stocker le statut
  chrome.storage.local.set({ apiOnline: isOnline });
});

// Écouter les messages du content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "predict") {
    handlePrediction(request.crashHistory)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true; // Async response
  }
  
  if (request.action === "checkStatus") {
    checkApiStatus().then(isOnline => {
      sendResponse({ online: isOnline });
    });
    return true;
  }
});

/**
 * Gérer la prédiction
 */
async function handlePrediction(crashHistory) {
  try {
    // Préparer les features
    const features = prepareFeatures(crashHistory);
    
    // Faire la prédiction
    const prediction = await makePrediction(features);
    
    return {
      success: true,
      prediction: prediction.prediction,
      confidence: prediction.confidence,
      signal: prediction.signal,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}
```

---

### content.js - Injection dans la page

```javascript
// Exemple: Capturer les valeurs de crash depuis la page du jeu
let crashHistory = [];

/**
 * Observer les changements dans la page et capturer les valeurs de crash
 */
function observeCrashValues() {
  // Adapter selon la structure de la page du jeu
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      // Logique pour extraire la valeur de crash
      const crashElement = document.querySelector(".crash-value");
      if (crashElement) {
        const crashValue = parseFloat(crashElement.textContent);
        if (!isNaN(crashValue)) {
          crashHistory.unshift(crashValue);
          // Garder seulement les 10 derniers
          if (crashHistory.length > 10) {
            crashHistory = crashHistory.slice(0, 10);
          }
          
          // Envoyer au background pour prédiction
          requestPrediction();
        }
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

/**
 * Demander une prédiction au background
 */
function requestPrediction() {
  if (crashHistory.length >= 3) {
    chrome.runtime.sendMessage(
      {
        action: "predict",
        crashHistory: crashHistory,
      },
      (response) => {
        if (response.success) {
          displayPrediction(response);
        } else {
          console.error("Prediction failed:", response.error);
        }
      }
    );
  }
}

/**
 * Afficher la prédiction sur la page
 */
function displayPrediction(prediction) {
  // Créer ou mettre à jour un élément d'affichage
  let displayElement = document.getElementById("crash-ai-prediction");
  
  if (!displayElement) {
    displayElement = document.createElement("div");
    displayElement.id = "crash-ai-prediction";
    displayElement.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 15px;
      border-radius: 10px;
      font-family: Arial, sans-serif;
      z-index: 10000;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    `;
    document.body.appendChild(displayElement);
  }
  
  const signalColor = prediction.signal.includes("PRUDENTE") ? "#4caf50" : "#ff9800";
  
  displayElement.innerHTML = `
    <div style="font-weight: bold; margin-bottom: 5px;">
      🤖 Crash AI
    </div>
    <div style="font-size: 14px;">
      Signal: <span style="color: ${signalColor}; font-weight: bold;">
        ${prediction.signal}
      </span>
    </div>
    <div style="font-size: 12px; opacity: 0.9;">
      Confidence: ${(prediction.confidence * 100).toFixed(1)}%
    </div>
  `;
}

// Démarrer l'observation
observeCrashValues();
```

---

### popup.html - Interface popup

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Crash AI Assistant</title>
  <style>
    body {
      width: 300px;
      padding: 20px;
      font-family: 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    h1 {
      font-size: 18px;
      margin: 0 0 15px 0;
      text-align: center;
    }
    .status {
      background: rgba(255,255,255,0.2);
      padding: 10px;
      border-radius: 8px;
      margin-bottom: 15px;
      text-align: center;
    }
    .prediction {
      background: rgba(255,255,255,0.3);
      padding: 15px;
      border-radius: 8px;
      margin-bottom: 15px;
    }
    .signal {
      font-size: 20px;
      font-weight: bold;
      margin: 10px 0;
    }
    .confidence {
      font-size: 14px;
      opacity: 0.9;
    }
    button {
      width: 100%;
      padding: 10px;
      border: none;
      border-radius: 5px;
      background: white;
      color: #667eea;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover {
      background: #f0f0f0;
    }
  </style>
</head>
<body>
  <h1>🤖 Crash AI Assistant</h1>
  
  <div class="status" id="status">
    Vérification...
  </div>
  
  <div class="prediction" id="prediction" style="display: none;">
    <div class="signal" id="signal"></div>
    <div class="confidence" id="confidence"></div>
  </div>
  
  <button id="refreshBtn">Actualiser</button>
  
  <script src="popup.js"></script>
</body>
</html>
```

---

### popup.js - Logique popup

```javascript
// Vérifier le statut au chargement
document.addEventListener("DOMContentLoaded", () => {
  checkStatus();
});

document.getElementById("refreshBtn").addEventListener("click", () => {
  checkStatus();
});

function checkStatus() {
  chrome.runtime.sendMessage(
    { action: "checkStatus" },
    (response) => {
      const statusElement = document.getElementById("status");
      if (response.online) {
        statusElement.textContent = "✅ API en ligne";
        statusElement.style.background = "rgba(76, 175, 80, 0.3)";
      } else {
        statusElement.textContent = "❌ API hors ligne";
        statusElement.style.background = "rgba(244, 67, 54, 0.3)";
      }
    }
  );
}
```

---

## ⚠️ Gestion des erreurs

### Types d'erreurs possibles

1. **API hors ligne**
   - Code: Erreur réseau
   - Solution: Afficher un message à l'utilisateur, réessayer plus tard

2. **Données insuffisantes**
   - Code: Erreur de validation
   - Solution: Attendre plus de données de crash

3. **Timeout**
   - Code: Erreur de timeout
   - Solution: Augmenter le timeout ou afficher un message

### Exemple de gestion d'erreurs

```javascript
async function safePrediction(crashHistory) {
  try {
    // Vérifier si on a assez de données
    if (crashHistory.length < 3) {
      throw new Error("Pas assez de données (min 3)");
    }
    
    // Tenter la prédiction avec timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prepareFeatures(crashHistory)),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      console.error("Request timeout");
      return { error: "Timeout - Réessayez" };
    }
    console.error("Prediction error:", error);
    return { error: error.message };
  }
}
```

---

## 🔒 Sécurité

### Points de sécurité

1. **HTTPS uniquement**
   - L'API utilise HTTPS automatiquement
   - Pas de données en clair

2. **CORS activé**
   - L'extension peut appeler l'API
   - Pas de restrictions d'origine

3. **Pas de données sensibles**
   - Seules les features numériques sont envoyées
   - Pas de données personnelles

4. **Endpoint /train protégé**
   - Nécessite une clé API
   - L'extension ne doit pas l'utiliser

---

## ⚡ Performance

### Optimisations

1. **Mise en cache des prédictions**
   ```javascript
   const predictionCache = new Map();
   
   function getCachedPrediction(featuresKey) {
     return predictionCache.get(featuresKey);
   }
   
   function setCachedPrediction(featuresKey, prediction) {
     predictionCache.set(featuresKey, prediction);
     // Expire après 30 secondes
     setTimeout(() => predictionCache.delete(featuresKey), 30000);
   }
   ```

2. **Rate limiting**
   ```javascript
   let lastPredictionTime = 0;
   const MIN_INTERVAL = 1000; // 1 seconde minimum
   
   async function rateLimitedPrediction(crashHistory) {
     const now = Date.now();
     if (now - lastPredictionTime < MIN_INTERVAL) {
       throw new Error("Trop de requêtes");
     }
     lastPredictionTime = now;
     return makePrediction(crashHistory);
   }
   ```

3. **Batch processing**
   - Regrouper plusieurs prédictions si nécessaire

---

## 🧪 Tests

### Test manuel dans la console

```javascript
// Test 1: Vérifier le statut
fetch("https://crashaiapi.onrender.com/")
  .then(r => r.json())
  .then(console.log);

// Test 2: Faire une prédiction
fetch("https://crashaiapi.onrender.com/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    hour: 4,
    minute: 49,
    second: 12,
    prev_1: 5.33,
    prev_2: 1.42,
    prev_3: 2.31,
    avg_5: 2.13,
    low_count_5: 2,
    high_count_10: 1
  })
})
  .then(r => r.json())
  .then(console.log);
```

---

## 📝 Checklist de déploiement

- [ ] Configurer `manifest.json` avec les permissions
- [ ] Implémenter `utils/api.js` avec les fonctions API
- [ ] Implémenter `utils/features.js` pour le calcul des features
- [ ] Créer `background.js` pour les appels API
- [ ] Créer `content.js` pour l'injection dans la page
- [ ] Créer `popup.html` et `popup.js` pour l'interface
- [ ] Tester localement avec `chrome://extensions`
- [ ] Tester sur la page du jeu cible
- [ ] Vérifier la gestion des erreurs
- [ ] Vérifier les performances
- [ ] Publier sur le Chrome Web Store

---

## 🆘 Support

**URL API:** https://crashaiapi.onrender.com  
**Documentation:** https://crashaiapi.onrender.com/documentation  
**Swagger UI:** https://crashaiapi.onrender.com/docs

**Projet:** Crash AI API - Signé SOLITAIRE HACK 🇨🇮

---

## 📄 License

Ce projet est une IA statistique d'aide à l'analyse uniquement. Il ne doit jamais promettre une prédiction garantie ou un gain certain. Les jeux de hasard comportent des risques importants.
