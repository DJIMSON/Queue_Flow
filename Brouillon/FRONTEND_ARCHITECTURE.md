# 🚀 QUEUEFLOW - ARCHITECTURE FRONTEND COMPLETE

## 📋 Vue d'ensemble

Ce document fournit l'architecture complète et professionnelle pour le frontend QueueFlow connecté à l'API Railway.

**API Backend**: https://queueflow-production.up.railway.app
**Documentation API**: https://queueflow-production.up.railway.app/docs

---

## 🏗️ ARCHITECTURE PROFESSIONNELLE

### 1. API Service Layer (Centralisé)
```javascript
const API_URL = 'https://queueflow-production.up.railway.app';
let authToken = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('user') || 'null');

async function apiCall(endpoint, method = 'GET', data = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
    
    const config = { method, headers };
    if (data) config.body = JSON.stringify(data);
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'Erreur API');
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
```

### 2. State Management
- **Token JWT**: Stocké dans localStorage pour persistance
- **Current User**: Objet utilisateur global
- **Auto-login**: Vérifie le token au chargement

### 3. Authentication
