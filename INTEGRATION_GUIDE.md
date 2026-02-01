# 🔗 Guide d'Intégration API - QueueFlow

## 📋 Vue d'Ensemble

Ce guide vous explique comment connecter votre `QueueFlow.html` existant au backend FastAPI en utilisant `api-connector.js`.

---

## 🚀 Étape 1 : Inclure le Connecteur

Dans votre fichier `QueueFlow.html`, ajoutez cette ligne **AVANT** votre balise `<script>` principale :

```html
<!-- Juste avant </body> -->
<script src="api-connector.js"></script>
<script>
    // Votre code JavaScript existant ici
</script>
</body>
```

---

## 🔧 Étape 2 : Modifier les Fonctions Existantes

### 2.1 Remplacer `initializeUsers()`

**ANCIEN CODE** (données statiques) :
```javascript
function initializeUsers() {
    users = [
        { id: 1, name: "Admin", email: "admin@queue.sn", password: "admin", role: "admin" },
        // ...
    ];
}
```

**NOUVEAU CODE** (backend) :
```javascript
function initializeUsers() {
    // Les utilisateurs sont gérés par le backend
    // Charger l'utilisateur connecté depuis localStorage
    const user = QueueFlowAPI.getCurrentUser();
    if (user) {
        currentUser = user;
        console.log('Utilisateur connecté:', user.name);
    }
}
```

---

### 2.2 Modifier la fonction `login()`

**ANCIEN CODE** :
```javascript
function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    const user = users.find(u => u.email === email && u.password === password);
    if (user) {
        currentUser = user;
        // ...
    }
}
```

**NOUVEAU CODE** :
```javascript
async function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        // Appel API
        const user = await QueueFlowAPI.login(email, password);

        currentUser = user;
        renderApp();
        alert(`Bienvenue ${user.name} !`);
    } catch (error) {
        alert('Email ou mot de passe incorrect');
        console.error(error);
    }
}
```

---

### 2.3 Modifier la fonction `signup()`

**ANCIEN CODE** :
```javascript
function signup() {
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    const newUser = {
        id: users.length + 1,
        name, email, password,
        role: 'citizen'
    };
    users.push(newUser);
}
```

**NOUVEAU CODE** :
```javascript
async function signup() {
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    try {
        // Appel API
        const user = await QueueFlowAPI.signup({
            name,
            email,
            password,
            role: 'citizen'
        });

        currentUser = user;
        renderApp();
        alert(`Compte créé avec succès ! Bienvenue ${user.name}`);
    } catch (error) {
        alert(`Erreur : ${error.message}`);
        console.error(error);
    }
}
```

---

### 2.4 Modifier la fonction `logout()`

**ANCIEN CODE** :
```javascript
function logout() {
    currentUser = null;
    renderApp();
}
```

**NOUVEAU CODE** :
```javascript
function logout() {
    QueueFlowAPI.logout(); // Supprime de localStorage
    currentUser = null;
    renderApp();
}
```

---

### 2.5 Charger les Institutions depuis l'API

**ANCIEN CODE** (données statiques) :
```javascript
const institutions = {
    hospital: [
        { id: 1, name: "Hôpital Aristide Le Dantec", location: "Dakar" },
        // ...
    ]
};

function populateInstitutions() {
    // Utilise les données statiques
}
```

**NOUVEAU CODE** (backend) :
```javascript
let institutions = {}; // Sera rempli par l'API

async function populateInstitutions() {
    try {
        // Charger depuis le backend
        institutions = await QueueFlowAPI.loadInstitutionsFromAPI();

        // Votre logique d'affichage existante
        // institutions.hospital, institutions.mairie, etc.

    } catch (error) {
        console.error('Erreur chargement institutions:', error);
        alert('Impossible de charger les institutions');
    }
}
```

---

### 2.6 Créer un Ticket avec l'API

**ANCIEN CODE** :
```javascript
function takeTicket(institutionId) {
    const ticketNumber = generateTicketNumber();
    const ticket = {
        id: tickets.length + 1,
        number: ticketNumber,
        institutionId,
        userId: currentUser.id,
        status: 'waiting'
    };
    tickets.push(ticket);
}
```

**NOUVEAU CODE** :
```javascript
async function takeTicket(institutionId) {
    try {
        const userId = currentUser ? currentUser.id : null;

        // Appel API
        const ticketData = await QueueFlowAPI.createTicket(institutionId, userId);

        // Afficher le ticket créé
        alert(`Ticket créé : ${ticketData.ticket_number}\n` +
              `Position : ${ticketData.queue_position}\n` +
              `Temps d'attente : ${ticketData.estimated_wait_time} min`);

        // Mettre à jour l'affichage
        displayTicket(ticketData);

    } catch (error) {
        alert(`Erreur : ${error.message}`);
        console.error(error);
    }
}
```

---

### 2.7 Vérifier un Ticket

**ANCIEN CODE** :
```javascript
function verifyTicket(ticketNumber) {
    const ticket = tickets.find(t => t.number === ticketNumber);
    if (ticket) {
        // Afficher infos
    }
}
```

**NOUVEAU CODE** :
```javascript
async function verifyTicket(ticketNumber) {
    try {
        // Appel API
        const stats = await QueueFlowAPI.getTicketStats(ticketNumber);

        alert(`Ticket : ${stats.ticket_number}\n` +
              `Position : ${stats.queue_position}\n` +
              `Temps d'attente : ${stats.estimated_wait_time} min\n` +
              `Institution : ${stats.institution_name}`);

    } catch (error) {
        alert('Ticket non trouvé');
        console.error(error);
    }
}
```

---

### 2.8 Opérateur : Appeler le Prochain Ticket

**NOUVEAU CODE** :
```javascript
async function callNextPatient() {
    if (!currentUser || currentUser.role !== 'operator') {
        alert('Action réservée aux opérateurs');
        return;
    }

    try {
        const institutionId = currentUser.institution_id;
        const operatorId = currentUser.id;

        // Appel API
        const result = await QueueFlowAPI.callNextTicket(institutionId, operatorId);

        if (result.ticket) {
            alert(`Ticket ${result.ticket.ticket_number} appelé !`);
            displayCurrentTicket(result.ticket);
        } else {
            alert(result.message); // "Aucun ticket en attente"
        }

    } catch (error) {
        alert(`Erreur : ${error.message}`);
        console.error(error);
    }
}
```

---

### 2.9 Opérateur : Compléter un Ticket

**NOUVEAU CODE** :
```javascript
async function completeCurrentTicket(ticketNumber) {
    if (!currentUser || currentUser.role !== 'operator') {
        alert('Action réservée aux opérateurs');
        return;
    }

    try {
        const operatorId = currentUser.id;

        // Appel API
        await QueueFlowAPI.completeTicket(ticketNumber, operatorId);

        alert('Ticket complété avec succès !');

        // Appeler automatiquement le suivant
        callNextPatient();

    } catch (error) {
        alert(`Erreur : ${error.message}`);
        console.error(error);
    }
}
```

---

### 2.10 Admin : Afficher les Statistiques

**NOUVEAU CODE** :
```javascript
async function displayAdminStats() {
    if (!currentUser || currentUser.role !== 'admin') {
        alert('Action réservée aux administrateurs');
        return;
    }

    try {
        // Appel API
        const stats = await QueueFlowAPI.getAdminStats();

        // Afficher les statistiques
        document.getElementById('adminTotalTickets').textContent = stats.total_tickets_today;
        document.getElementById('adminWaitingTickets').textContent = stats.tickets_waiting;
        document.getElementById('adminCompletedTickets').textContent = stats.tickets_completed;
        document.getElementById('adminMissedRate').textContent = 
            `${((stats.tickets_missed / stats.total_tickets_today) * 100).toFixed(1)}%`;

    } catch (error) {
        console.error('Erreur stats admin:', error);
    }
}
```

---

### 2.11 Charger l'Historique des Tickets

**NOUVEAU CODE** :
```javascript
async function loadUserTicketHistory() {
    if (!currentUser) return;

    try {
        // Appel API
        const tickets = await QueueFlowAPI.getUserTickets(currentUser.id);

        // Afficher l'historique
        const historyContainer = document.getElementById('citizenHistoryDisplay');
        historyContainer.innerHTML = '';

        tickets.forEach(ticket => {
            const ticketEl = document.createElement('div');
            ticketEl.className = 'ticket-history-item';
            ticketEl.innerHTML = `
                <strong>${ticket.ticket_number}</strong> - 
                ${ticket.institution.name} - 
                <span class="status-${ticket.status}">${ticket.status}</span>
                <br>
                <small>${new Date(ticket.created_at).toLocaleString()}</small>
            `;
            historyContainer.appendChild(ticketEl);
        });

    } catch (error) {
        console.error('Erreur historique:', error);
    }
}
```

---

## 📊 Exemple Complet d'Intégration

Voici un exemple complet de votre HTML avec le connecteur intégré :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>QueueFlow</title>
    <!-- Vos styles CSS -->
</head>
<body>
    <!-- Votre contenu HTML existant -->

    <!-- ÉTAPE 1 : Inclure le connecteur API -->
    <script src="api-connector.js"></script>

    <!-- ÉTAPE 2 : Votre script principal modifié -->
    <script>
        let currentUser = null;
        let institutions = {};

        // Au chargement de la page
        window.addEventListener('DOMContentLoaded', async () => {
            initializeApp();
        });

        async function initializeApp() {
            // Charger l'utilisateur connecté
            currentUser = QueueFlowAPI.getCurrentUser();

            // Charger les institutions depuis l'API
            await populateInstitutions();

            // Rendre l'interface
            renderApp();
        }

        async function populateInstitutions() {
            try {
                institutions = await QueueFlowAPI.loadInstitutionsFromAPI();
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        async function login() {
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            try {
                currentUser = await QueueFlowAPI.login(email, password);
                renderApp();
            } catch (error) {
                alert('Erreur de connexion');
            }
        }

        // Autres fonctions...

    </script>
</body>
</html>
```

---

## ✅ Checklist d'Intégration

- [ ] Inclure `api-connector.js` dans le HTML
- [ ] Modifier `initializeUsers()` pour utiliser localStorage
- [ ] Modifier `login()` pour appeler l'API
- [ ] Modifier `signup()` pour appeler l'API
- [ ] Modifier `logout()` pour utiliser l'API
- [ ] Charger les institutions depuis l'API au démarrage
- [ ] Modifier la création de tickets pour utiliser l'API
- [ ] Modifier la vérification de tickets pour utiliser l'API
- [ ] Ajouter les fonctions opérateur (appeler/compléter tickets)
- [ ] Ajouter l'affichage des statistiques admin
- [ ] Tester chaque fonctionnalité

---

## 🧪 Test des Fonctionnalités

### Test 1 : Authentification
1. Ouvrir `QueueFlow.html` dans le navigateur
2. Créer un compte via le formulaire signup
3. Se déconnecter et se reconnecter
4. Vérifier que l'utilisateur reste connecté après refresh

### Test 2 : Créer un Ticket
1. Se connecter comme citoyen
2. Choisir une institution
3. Créer un ticket
4. Vérifier que le numéro est généré par le backend (H001, M001, etc.)

### Test 3 : Opérateur
1. Se connecter avec : `operator@hopital.sn` / `operator123`
2. Appeler le premier ticket
3. Le compléter
4. Appeler le suivant

### Test 4 : Admin
1. Se connecter avec : `admin@queueflow.sn` / `admin123`
2. Voir les statistiques globales
3. Lister les opérateurs

---

## 🐛 Dépannage

### Erreur : "CORS policy"
**Solution** : Le backend a déjà CORS activé. Vérifiez que le backend est lancé.

### Erreur : "Failed to fetch"
**Solution** : Vérifiez que le backend tourne sur http://localhost:8000

### Les données ne s'affichent pas
**Solution** : Ouvrez la console (F12) et regardez les erreurs

### L'utilisateur est déconnecté au refresh
**Solution** : Appelez `QueueFlowAPI.getCurrentUser()` au chargement de la page

---

## 📞 API Reference Rapide

```javascript
// Auth
await QueueFlowAPI.signup({ name, email, password, role });
await QueueFlowAPI.login(email, password);
QueueFlowAPI.logout();
const user = QueueFlowAPI.getCurrentUser();

// Institutions
const all = await QueueFlowAPI.getAllInstitutions();
const hospitals = await QueueFlowAPI.getInstitutionsByType('hospital');

// Tickets
const ticket = await QueueFlowAPI.createTicket(institutionId, userId);
const stats = await QueueFlowAPI.getTicketStats('H001');
const history = await QueueFlowAPI.getUserTickets(userId);

// Opérateur
const next = await QueueFlowAPI.callNextTicket(instId, opId);
await QueueFlowAPI.completeTicket('H001', opId);

// Admin
const stats = await QueueFlowAPI.getAdminStats();
const operators = await QueueFlowAPI.getAllOperators();
```

---

**Votre frontend est maintenant connecté au backend ! 🎉**
