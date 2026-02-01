# 🚀 Guide d'Utilisation - QueueFlow Frontend + Backend

## 📋 Prérequis

Avant de commencer, assurez-vous que :
- ✅ Le backend est installé (`pip install -r requirements.txt`)
- ✅ L'API est lancée (`python run.py`)
- ✅ Le serveur tourne sur http://localhost:8000

## 🎯 Ouvrir le Frontend

### Option 1 : Double-clic (Recommandé)
1. Double-cliquez sur `QueueFlow-Connected.html`
2. Le fichier s'ouvre dans votre navigateur par défaut

### Option 2 : Depuis le navigateur
1. Ouvrez votre navigateur (Chrome, Firefox, Edge)
2. Faites Ctrl+O ou File > Open
3. Sélectionnez `QueueFlow-Connected.html`

## 🧪 Tester l'Application

### Test 1 : Créer un Ticket pour un Hôpital

1. **Page d'accueil** : Cliquez sur "Créer un Ticket"
2. **Sélection du type** : Cliquez sur "Hôpitaux"
   - Vous devriez voir la liste des hôpitaux de Dakar
   - Les données viennent du backend en temps réel
3. **Sélection de l'hôpital** : Cliquez sur un hôpital (ex: Hôpital Principal de Dakar)
4. **Ticket créé** : Vous recevez :
   - Numéro de ticket (ex: H001)
   - Position dans la file
   - Temps d'attente estimé
   - Nombre de personnes devant vous

### Test 2 : Vérifier un Ticket

1. **Page d'accueil** : Cliquez sur "Vérifier un Ticket"
2. **Saisir le numéro** : Entrez le numéro reçu (ex: H001)
3. **Vérification** : Cliquez sur "Vérifier" ou appuyez sur Entrée
4. **Résultat** : Une popup affiche le statut actuel du ticket

### Test 3 : Créer Plusieurs Tickets

1. Créez un premier ticket pour l'Hôpital Principal
   - Vous êtes en position 1
2. Créez un second ticket pour le même hôpital
   - Vous êtes en position 2
   - Le temps d'attente augmente
3. Vérifiez le premier ticket
   - La position reste 1

## 🔍 Fonctionnalités en Détail

### Affichage des Institutions par Type

**Hôpitaux** (Type: hospital)
- Hôpital Aristide Le Dantec
- Hôpital Principal de Dakar
- Hôpital Fann
- Hôpital Abass Ndao
- Clinique Cheikh Zaid

**Mairies** (Type: mairie)
- Mairie de Dakar
- Mairie de Pikine
- Mairie de Guédiawaye

**Banques** (Type: banque)
- SGBS (Société Générale)
- BOA Sénégal

**Transports** (Type: transport)
- Gare Routière de Dakar
- Gare Routière Pompiers

### Système de Numérotation des Tickets

- **H001, H002...** : Hôpitaux
- **M001, M002...** : Mairies
- **B001, B002...** : Banques
- **T001, T002...** : Transports

Le numéro augmente pour chaque institution indépendamment.

### Calcul du Temps d'Attente

- **Temps moyen de service** : 3 minutes par défaut
- **Formule** : Personnes devant vous × 3 minutes
- **Exemple** : 4 personnes devant = 12 minutes d'attente

## ⚠️ Résolution des Problèmes

### Problème 1 : "Erreur de chargement des institutions"

**Cause** : Le backend n'est pas démarré

**Solution** :
```bash
# Dans un terminal, dans le dossier du backend
python run.py
```

Vérifiez que vous voyez :
```
INFO: Started server process [xxxxx]
INFO: Application startup complete.
```

### Problème 2 : "Erreur lors de la création du ticket"

**Causes possibles** :
1. Backend arrêté → Relancez `python run.py`
2. Mauvaise URL API → Vérifiez dans le code : `const API_URL = 'http://localhost:8000'`
3. Port différent → Si votre backend est sur un autre port, modifiez l'URL

### Problème 3 : "Ticket non trouvé"

**Causes** :
1. Numéro de ticket incorrect (respectez les majuscules/minuscules)
2. Ticket créé sur une autre instance de la BD
3. Base de données réinitialisée

**Solution** : Créez un nouveau ticket et vérifiez-le immédiatement

### Problème 4 : CORS Error dans la Console

Si vous voyez dans la console du navigateur :
```
Access to fetch at 'http://localhost:8000/...' has been blocked by CORS policy
```

**Solution** : Le backend a déjà CORS activé. Si le problème persiste :
1. Vérifiez que le backend tourne bien
2. Utilisez Chrome/Firefox (pas IE ou anciens navigateurs)

## 🔧 Personnalisation

### Changer l'URL du Backend

Dans `QueueFlow-Connected.html`, ligne ~210 :
```javascript
const API_URL = 'http://localhost:8000';
```

Changez-la si votre backend est ailleurs :
```javascript
const API_URL = 'http://192.168.1.100:8000';  // Autre machine
const API_URL = 'https://monapi.com';         // Production
```

### Ajouter une Nouvelle Institution

**Via l'API** (Swagger) :
1. Ouvrez http://localhost:8000/docs
2. Trouvez `POST /institutions`
3. Cliquez "Try it out"
4. Remplissez le JSON :
```json
{
  "name": "Hôpital de Grand Yoff",
  "type": "hospital",
  "location": "Dakar",
  "address": "Grand Yoff, Dakar",
  "phone": "+221 33 XXX XX XX"
}
```
5. Execute

L'institution apparaîtra automatiquement dans le frontend !

## 📊 Voir les Statistiques

Ouvrez dans votre navigateur :
```
http://localhost:8000/stats
```

Vous verrez :
- Nombre total d'institutions
- Tickets créés au total
- Tickets en attente
- Tickets complétés

## 🎓 Comprendre le Flux de Données

### 1. Clic sur "Hôpitaux"
```
Frontend → GET /institutions/type/hospital → Backend
Backend → SQLite (query institutions) → JSON
JSON → Frontend → Affichage dans la grille
```

### 2. Clic sur un Hôpital
```
Frontend → POST /tickets {institution_id: 1} → Backend
Backend → Génère numéro (H001) → Calcule position → Sauvegarde BD
Backend → Renvoie {ticket_number, position, wait_time}
Frontend → Affiche le ticket
```

### 3. Vérification d'un Ticket
```
Frontend → GET /tickets/H001/stats → Backend
Backend → Query BD → Compte les tickets devant → Calcule temps
Backend → Renvoie les stats actualisées
Frontend → Affiche dans une popup
```

## 📱 Utilisation Mobile

Le frontend est responsive et fonctionne sur mobile !

Pour tester sur votre téléphone :
1. Assurez-vous que PC et téléphone sont sur le même WiFi
2. Trouvez l'IP de votre PC (cmd → ipconfig)
3. Modifiez l'API_URL dans le HTML :
   ```javascript
   const API_URL = 'http://192.168.1.XX:8000';
   ```
4. Ouvrez le fichier HTML sur votre téléphone via un serveur HTTP

## 🚀 Prochaines Étapes

1. **Tester toutes les fonctionnalités** une par une
2. **Créer des tickets** pour chaque type d'institution
3. **Vérifier** que les numéros augmentent correctement
4. **Observer** le calcul du temps d'attente
5. **Expérimenter** avec plusieurs tickets simultanés

## 💡 Astuces

- **F12** : Ouvre la console du navigateur pour voir les logs
- **Ctrl+Shift+R** : Rafraîchit la page en vidant le cache
- **Swagger** : http://localhost:8000/docs pour tester les APIs directement

---

**Félicitations ! Vous avez maintenant une application fullstack fonctionnelle !** 🎉
