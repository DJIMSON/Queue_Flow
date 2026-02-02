# 🚀 GUIDE COMPLET - POUSSER QUEUEFLOW SUR GITHUB

## 📋 ÉTAPE 1 : PRÉPARER LES FICHIERS

✅ Télécharge ces fichiers que je viens de créer :
1. .gitignore (pour ignorer les fichiers inutiles)
2. README.md (documentation du projet)

Place-les dans le dossier racine de ton projet.

---

## 🔧 ÉTAPE 2 : INSTALLER GIT (SI PAS DÉJÀ FAIT)

### Windows
Télécharge depuis : https://git-scm.com/download/win

### Linux
```bash
sudo apt-get update
sudo apt-get install git
```

### Vérifier l'installation
```bash
git --version
```

---

## 🎯 ÉTAPE 3 : CONFIGURER GIT

Ouvre un terminal dans le dossier QueueFlow :

```bash
# Configure ton nom
git config --global user.name "Maick Broco"

# Configure ton email GitHub
git config --global user.email "ton-email@example.com"
```

---

## 📦 ÉTAPE 4 : INITIALISER LE DÉPÔT LOCAL

```bash
# Initialise Git
git init

# Vérifie les fichiers
git status

# Ajoute tous les fichiers
git add .

# Crée le premier commit
git commit -m "Initial commit - QueueFlow v1.0"
```

---

## 🌐 ÉTAPE 5 : CRÉER LE DÉPÔT GITHUB

1. Va sur https://github.com
2. Clique sur le bouton vert **New** en haut à droite
3. Remplis :
   - Repository name : **QueueFlow**
   - Description : **Système de gestion de files d'attente moderne**
   - Visibilité : **Public**
   - ⚠️ NE COCHE PAS Initialize with README
4. Clique sur **Create repository**

---

## 🔗 ÉTAPE 6 : CONNECTER À GITHUB

```bash
# Remplace TON-USERNAME par ton nom d'utilisateur
git remote add origin https://github.com/TON-USERNAME/QueueFlow.git

# Vérifie
git remote -v
```

---

## 🚀 ÉTAPE 7 : POUSSER LE CODE

```bash
# Renomme la branche en main
git branch -M main

# Pousse le code
git push -u origin main
```

---

## 🔑 ÉTAPE 8 : TOKEN D'ACCÈS (SI DEMANDÉ)

Si GitHub demande un mot de passe :

1. Va sur https://github.com/settings/tokens
2. Generate new token (classic)
3. Nom : **QueueFlow Push**
4. Coche **repo**
5. Generate token
6. COPIE LE TOKEN
7. Utilise-le comme mot de passe

---

## ✅ ÉTAPE 9 : VÉRIFIER

Va sur https://github.com/TON-USERNAME/QueueFlow
Tu devrais voir tous tes fichiers !

---

## 🔄 POUR LES MODIFICATIONS FUTURES

```bash
git status          # Voir les changements
git add .           # Ajouter tous les fichiers
git commit -m "Description"  # Commit
git push            # Pousser
```

---

## 🐛 PROBLÈMES COURANTS

### remote origin already exists
```bash
git remote remove origin
git remote add origin https://github.com/TON-USERNAME/QueueFlow.git
```

### Authentication failed
Crée un token d'accès personnel (ÉTAPE 8)

### Fichier .db poussé par erreur
```bash
git rm --cached queueflow.db
git commit -m "Remove database"
git push
```

---

## ✅ CHECKLIST FINALE

- [ ] .gitignore créé
- [ ] README.md personnalisé
- [ ] requirements.txt présent
- [ ] .db dans .gitignore
- [ ] venv/ dans .gitignore
- [ ] Repository GitHub créé
- [ ] Code poussé avec succès

---

## 🎉 FÉLICITATIONS !

Ton projet est maintenant sur GitHub !

Partage avec : **https://github.com/TON-USERNAME/QueueFlow**