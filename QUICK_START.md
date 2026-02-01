# 🚀 Guide de Démarrage Rapide - Frontend Connecté

## ✅ Fichiers Créés

1. **QueueFlow-Connected.html** - Votre frontend avec les scripts API inclus
2. **api-connector.js** - Connecteur API de base
3. **queueflow-api-overrides.js** - Remplacement des fonctions

## 🎯 Comment Utiliser

### Option 1 : Tester Immédiatement

1. **Ouvrez QueueFlow-Connected.html dans votre navigateur**
   - Double-cliquez sur le fichier
   - Ou faites un clic droit → Ouvrir avec → Navigateur

2. **Vérifiez que le backend tourne**
   - Terminal doit afficher : `Uvicorn running on http://0.0.0.0:8000`

3. **Testez l'authentification**
   - Créez un compte ou connectez-vous avec :
     - Email : `admin@queueflow.sn`
     - Password : `admin123`

### Option 2 : Utiliser les Nouvelles Fonctions

Dans votre code HTML existant, vous pouvez maintenant utiliser :

#### Créer un Ticket
```javascript
// Au lieu de votre fonction actuelle, utilisez :
await createTicketAPI(institutionId);
```

#### Vérifier un Ticket
```javascript
// Remplacez par :
await verifyTicketAPI();
```

#### Opérateur : Appeler un Ticket
```javascript
await callNextTicketAPI();
```

#### Opérateur : Compléter un Ticket
```javascript
await completeTicketAPI(ticketNumber);
```

#### Admin : Voir les Stats
```javascript
await loadAdminStatsAPI();
```

#### Voir l'Historique
```javascript
await loadUserHistoryAPI();
```

## 🔧 Modifications à Faire (Optionnel)

Si vous voulez personnaliser davantage, modifiez dans votre script principal :

### 1. Lors de la création d'un ticket

**TROUVEZ** dans votre code (ligne ~1500-1800) :
```javascript
function takeTicket() {
    // Votre code actuel
}
```

**REMPLACEZ** par :
```javascript
async function takeTicket() {
    const institutionId = getSelectedInstitutionId(); // Votre fonction
    await createTicketAPI(institutionId);
}
```

### 2. Lors de la vérification d'un ticket

**TROUVEZ** :
```javascript
function verifyTicket() {
    // Votre code actuel
}
```

**REMPLACEZ** par :
```javascript
async function verifyTicket() {
    await verifyTicketAPI();
}
```

### 3. Pour les opérateurs

**AJOUTEZ** un bouton dans votre interface opérateur :
```html
<button onclick="callNextTicketAPI()">
    Appeler le Prochain Patient
</button>
```

### 4. Pour charger les institutions

**TROUVEZ** votre fonction populateInstitutions et **AJOUTEZ** au début :
```javascript
async function populateInstitutions() {
    // Charger depuis l'API
    institutions = await loadInstitutions();

    // Votre code d'affichage existant...
}
```

## 🧪 Tests à Effectuer

### Test 1 : Backend Connecté
1. Ouvrez la console (F12)
2. Vous devriez voir :
   ```
   ✅ QueueFlow API Connector chargé
   🔄 Chargement des overrides API...
   ✅ Overrides API chargés
   ```

### Test 2 : Créer un Compte
1. Cliquez sur "S'inscrire"
2. Remplissez le formulaire
3. Soumettez
4. Vérifiez la console pour voir : `✅ Compte créé: [votre nom]`

### Test 3 : Se Connecter
1. Utilisez : `admin@queueflow.sn` / `admin123`
2. Vérifiez : `✅ Connexion réussie: Admin QueueFlow`

### Test 4 : Créer un Ticket
1. Choisissez une institution
2. Appelez `createTicketAPI(1)` dans la console
3. Vous devriez voir les infos du ticket

### Test 5 : Opérateur
1. Connectez-vous avec : `operator@hopital.sn` / `operator123`
2. Dans la console : `await callNextTicketAPI()`
3. Devrait afficher le prochain ticket

## ⚠️ Dépannage

### Erreur CORS
- **Vérifiez** que le backend tourne sur http://localhost:8000
- **Solution** : Le backend a déjà CORS activé

### "QueueFlowAPI is not defined"
- **Vérifiez** que api-connector.js est bien inclus AVANT votre script
- **Solution** : L'ordre doit être :
  1. api-connector.js
  2. queueflow-api-overrides.js
  3. Votre script principal

### Les institutions ne se chargent pas
- **Ouvrez** la console et cherchez les erreurs
- **Vérifiez** : http://localhost:8000/institutions
- **Solution** : Attendez que `loadInstitutions()` finisse

### L'utilisateur n'est pas persistant
- **Problème** : L'utilisateur se déconnecte au refresh
- **Solution** : Appelez `initializeUsers()` au chargement :
```javascript
window.addEventListener('DOMContentLoaded', () => {
    initializeUsers();
    renderApp();
});
```

## 📊 Vérification Console

Ouvrez la console (F12) et tapez :
```javascript
// Voir l'utilisateur connecté
QueueFlowAPI.getCurrentUser()

// Tester une connexion
await QueueFlowAPI.login('admin@queueflow.sn', 'admin123')

// Voir toutes les institutions
await QueueFlowAPI.getAllInstitutions()

// Créer un ticket
await QueueFlowAPI.createTicket(1)

// Voir les stats admin
await QueueFlowAPI.getAdminStats()
```

## ✅ Résultat Attendu

Après intégration, votre application devrait :
- ✅ Charger les institutions depuis le backend
- ✅ Créer des comptes utilisateurs persistants
- ✅ Générer des tickets avec numéros uniques (H001, M002, etc.)
- ✅ Permettre aux opérateurs d'appeler des tickets
- ✅ Afficher les statistiques admin
- ✅ Garder l'utilisateur connecté après refresh

## 🎉 Prêt !

Votre frontend est maintenant **connecté au backend** !

**Pour démarrer** :
1. Backend lance : `python run.py`
2. Ouvrez : `QueueFlow-Connected.html`
3. Testez l'authentification et la création de tickets

**Documentation complète** : INTEGRATION_GUIDE.md
