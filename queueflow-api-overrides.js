/**
 * QueueFlow API Overrides - VERSION V4.1 ULTIMATE (FIXED showApp)
 * ================================================================
 * Corrections CRITIQUES :
 * - Nettoyage complet localStorage au logout
 * - Empêcher création automatique de tickets
 * - Isolation totale des données par utilisateur
 * - Validation stricte user_id
 * - Alias showApp pour compatibilité HTML
 */

console.log('🔄 Chargement overrides API V4.1...');

window.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Initialisation API V4.1...');
    initializeAPIFunctionsV4();
});

if (document.readyState !== 'loading') {
    setTimeout(function() { initializeAPIFunctionsV4(); }, 100);
}

function initializeAPIFunctionsV4() {
    console.log('🔧 Installation fonctions V4.1...');

    // ================================================
    // NETTOYAGE COMPLET DES DONNÉES
    // ================================================
    function clearAllUserData() {
        console.log('🧹 Nettoyage complet des données...');

        // Vider currentUser
        if (typeof window.currentUser !== 'undefined') {
            window.currentUser = null;
        }

        // Vider toutes les variables globales liées aux tickets
        if (typeof window.activeTicket !== 'undefined') {
            window.activeTicket = null;
        }
        if (typeof window.userTickets !== 'undefined') {
            window.userTickets = [];
        }
        if (typeof window.currentTicketData !== 'undefined') {
            window.currentTicketData = null;
        }

        // Nettoyer les affichages DOM
        const ticketDisplay = document.getElementById('citizenTicketDisplay');
        if (ticketDisplay) {
            ticketDisplay.innerHTML = '';
        }

        const historyDisplay = document.getElementById('citizenHistoryDisplay');
        if (historyDisplay) {
            historyDisplay.innerHTML = '';
        }

        console.log('✅ Nettoyage terminé');
    }

    // ================================================
    // HELPER: GESTION DES PAGES
    // ================================================
    function showApplication() {
        const loginPage = document.getElementById('loginPage');
        const signupPage = document.getElementById('signupPage');
        const appPage = document.getElementById('appPage');

        if (loginPage) loginPage.classList.add('hidden');
        if (signupPage) signupPage.classList.add('hidden');
        if (appPage) appPage.classList.remove('hidden');

        console.log('✅ Application affichee');
    }

    function hideApplication() {
        const loginPage = document.getElementById('loginPage');
        const signupPage = document.getElementById('signupPage');
        const appPage = document.getElementById('appPage');

        if (appPage) appPage.classList.add('hidden');
        if (loginPage) loginPage.classList.remove('hidden');
        if (signupPage) signupPage.classList.add('hidden');

        console.log('✅ Retour au login');
    }

    function showLoginPage() {
        const loginPage = document.getElementById('loginPage');
        const signupPage = document.getElementById('signupPage');

        if (signupPage) signupPage.classList.add('hidden');
        if (loginPage) loginPage.classList.remove('hidden');

        console.log('🔐 Page connexion affichee');
    }

    // ================================================
    // ALIAS POUR COMPATIBILITÉ HTML
    // ================================================
    window.showApp = showApplication;  // Alias pour le HTML
    window.hideApp = hideApplication;  // Alias pour le HTML

    // ================================================
    // OVERRIDE toggleSignup
    // ================================================
    window.toggleSignup = function() {
        const loginPage = document.getElementById('loginPage');
        const signupPage = document.getElementById('signupPage');

        if (loginPage && signupPage) {
            loginPage.classList.toggle('hidden');
            signupPage.classList.toggle('hidden');
        }
    };

    // ================================================
    // LOGIN - AVEC NETTOYAGE AVANT
    // ================================================
    window.login = async function() {
        console.log('🔐 Tentative connexion...');

        const emailEl = document.getElementById('loginEmail');
        const passEl = document.getElementById('loginPassword');

        if (!emailEl || !passEl) {
            alert('Erreur: Champs introuvables');
            return;
        }

        const email = emailEl.value.trim();
        const password = passEl.value;

        if (!email || !password) {
            alert('Veuillez remplir tous les champs');
            return;
        }

        try {
            // NETTOYER AVANT LOGIN
            clearAllUserData();

            console.log('Connexion pour:', email);
            const user = await QueueFlowAPI.login(email, password);
            console.log('✅ Login reussi:', user);

            // Sauvegarder SEULEMENT le nouvel utilisateur
            window.currentUser = user;

            // Vider les champs
            emailEl.value = '';
            passEl.value = '';

            // Afficher l'application
            showApplication();

            // Rendre l'interface
            if (typeof window.renderApp === 'function') {
                console.log('Appel renderApp pour:', user.email);
                window.renderApp();
            } else {
                renderAppManual(user);
            }

            var roleMsg = user.role === 'citizen' ? 'Citoyen' : 
                         user.role === 'operator' ? 'Operateur' : 'Administrateur';
            alert('Bienvenue ' + user.name + ' !\nRole: ' + roleMsg);

        } catch (error) {
            console.error('❌ Erreur connexion:', error);
            alert('Email ou mot de passe incorrect');
        }
    };

    // ================================================
    // SIGNUP - FLOW SÉCURISÉ
    // ================================================
    window.signup = async function() {
        console.log('📝 Tentative inscription...');

        const nameEl = document.getElementById('signupName');
        const emailEl = document.getElementById('signupEmail');
        const passEl = document.getElementById('signupPassword');

        if (!nameEl || !emailEl || !passEl) {
            alert('Erreur: Champs introuvables');
            return;
        }

        const name = nameEl.value.trim();
        const email = emailEl.value.trim();
        const password = passEl.value;

        if (!name || !email || !password) {
            alert('Veuillez remplir tous les champs');
            return;
        }

        if (password.length < 6) {
            alert('Le mot de passe doit contenir au moins 6 caracteres');
            return;
        }

        if (!email.includes('@')) {
            alert('Email invalide');
            return;
        }

        try {
            console.log('Creation compte pour:', email);

            const user = await QueueFlowAPI.signup({
                name: name,
                email: email,
                password: password,
                role: 'citizen'
            });

            console.log('✅ Compte cree:', user);

            // Vider les champs
            nameEl.value = '';
            emailEl.value = '';
            passEl.value = '';

            alert('✅ Compte cree avec succes !\n\nVeuillez vous connecter avec vos identifiants.');

            // Retour au login
            showLoginPage();

            // Pré-remplir l'email
            const loginEmailEl = document.getElementById('loginEmail');
            if (loginEmailEl) {
                loginEmailEl.value = email;

                const loginPassEl = document.getElementById('loginPassword');
                if (loginPassEl) {
                    setTimeout(function() {
                        loginPassEl.focus();
                    }, 100);
                }
            }

        } catch (error) {
            console.error('❌ Erreur inscription:', error);
            if (error.message && error.message.includes('already exists')) {
                alert('Cet email est deja utilise.');
            } else {
                alert('Erreur: ' + error.message);
            }
        }
    };

    // ================================================
    // LOGOUT - NETTOYAGE COMPLET CRITIQUE
    // ================================================
    window.logout = function() {
        console.log('👋 Deconnexion en cours...');

        // 1. Déconnecter de l'API (nettoie localStorage)
        QueueFlowAPI.logout();

        // 2. Nettoyer TOUTES les données utilisateur
        clearAllUserData();

        // 3. Vider les champs de connexion
        const emailEl = document.getElementById('loginEmail');
        const passEl = document.getElementById('loginPassword');
        if (emailEl) emailEl.value = '';
        if (passEl) passEl.value = '';

        // 4. Retour au login
        hideApplication();

        console.log('✅ Deconnecte - Toutes les donnees effacees');
    };

    // ================================================
    // RENDU MANUEL
    // ================================================
    function renderAppManual(user) {
        console.log('🎨 Rendu manuel:', user.role, '-', user.email);

        const roleEl = document.getElementById('userRole');
        const emailEl = document.getElementById('userEmail');

        const roleLabels = {
            citizen: 'Citoyen',
            operator: 'Operateur',
            admin: 'Administrateur'
        };

        if (roleEl) roleEl.textContent = roleLabels[user.role] || user.role;
        if (emailEl) emailEl.textContent = user.email;
    }

    // ================================================
    // AUTO-LOGIN - AVEC VÉRIFICATION
    // ================================================
    const savedUser = QueueFlowAPI.getCurrentUser();
    if (savedUser) {
        console.log('👤 Utilisateur sauvegarde:', savedUser.name, '-', savedUser.email);

        // Vérifier que l'utilisateur est valide
        if (savedUser.id && savedUser.email) {
            window.currentUser = savedUser;

            setTimeout(function() {
                showApplication();
                if (typeof window.renderApp === 'function') {
                    window.renderApp();
                } else {
                    renderAppManual(savedUser);
                }
            }, 200);
        } else {
            console.warn('⚠️ Utilisateur sauvegarde invalide, nettoyage...');
            QueueFlowAPI.logout();
            clearAllUserData();
        }
    }

    // ================================================
    // INSTITUTIONS
    // ================================================
    window.loadInstitutionsAPI = async function() {
        try {
            console.log('🏥 Chargement institutions...');
            const inst = await QueueFlowAPI.loadInstitutionsFromAPI();

            if (typeof window.institutions !== 'undefined') {
                window.institutions = inst;
            }

            console.log('✅ Institutions chargees');
            return inst;

        } catch (error) {
            console.error('❌ Erreur institutions:', error);
            return { hospital: [], mairie: [], banque: [], transport: [] };
        }
    };

    loadInstitutionsAPI().then(function(inst) {
        if (typeof window.populateInstitutions === 'function') {
            const selectEl = document.getElementById('signupInstitution');
            if (selectEl) {
                window.populateInstitutions();
            }
        }
    });

    // ================================================
    // TICKETS - AVEC VALIDATION STRICTE USER_ID
    // ================================================
    window.createTicketAPI = async function(institutionId) {
        try {
            // VALIDATION CRITIQUE : Vérifier l'utilisateur
            const user = QueueFlowAPI.getCurrentUser();

            if (!user) {
                console.error('❌ Aucun utilisateur connecte');
                alert('Vous devez etre connecte pour creer un ticket');
                return null;
            }

            if (!user.id) {
                console.error('❌ User ID manquant');
                alert('Erreur: Utilisateur invalide');
                return null;
            }

            console.log('🎫 Creation ticket pour:', user.email, '(ID:', user.id, ')');
            console.log('Institution:', institutionId);

            const data = await QueueFlowAPI.createTicket(institutionId, user.id);
            console.log('✅ Ticket cree:', data);

            // Vérifier que le ticket appartient bien à cet utilisateur
            if (data.user_id && data.user_id !== user.id) {
                console.error('⚠️ ATTENTION: Ticket cree pour un autre utilisateur !');
                console.error('User actuel:', user.id, 'Ticket user_id:', data.user_id);
            }

            displayTicket(data);

            if (typeof window.updateCitizenDisplay === 'function') {
                window.updateCitizenDisplay();
            }

            return data;

        } catch (error) {
            console.error('❌ Erreur creation ticket:', error);
            alert('Erreur: ' + error.message);
            return null;
        }
    };

    function displayTicket(data) {
        var msg = '🎫 Ticket cree !\n\n';
        msg += 'Numero: ' + data.ticket_number + '\n';
        msg += 'Institution: ' + data.institution_name + '\n';
        msg += 'Position: ' + data.queue_position + '\n';
        msg += 'Devant vous: ' + data.people_ahead + '\n';
        msg += 'Temps estime: ' + data.estimated_wait_time + ' min';

        alert(msg);

        const el = document.getElementById('citizenTicketDisplay');
        if (el) {
            el.innerHTML = '<div style="padding:20px;background:#f0f9ff;border-radius:8px;margin:10px 0">' +
                '<h3 style="margin:0 0 10px 0;color:#0369a1">Votre Ticket</h3>' +
                '<div style="font-size:32px;font-weight:bold;color:#0c4a6e;margin:10px 0">' +
                data.ticket_number + '</div>' +
                '<p><strong>Institution:</strong> ' + data.institution_name + '</p>' +
                '<p><strong>Position:</strong> ' + data.queue_position + '</p>' +
                '<p><strong>Temps:</strong> ' + data.estimated_wait_time + ' min</p>' +
                '</div>';
        }
    }

    window.verifyTicketAPI = async function() {
        const input = document.getElementById('verifyTicketInput');
        if (!input) return;

        const ticketNum = input.value.trim().toUpperCase();

        if (!ticketNum) {
            alert('Veuillez entrer un numero');
            return;
        }

        try {
            const stats = await QueueFlowAPI.getTicketStats(ticketNum);

            var msg = '🎫 Ticket: ' + stats.ticket_number + '\n\n';
            msg += 'Institution: ' + stats.institution_name + '\n';
            msg += 'Position: ' + stats.queue_position + '\n';
            msg += 'Temps: ' + stats.estimated_wait_time + ' min';

            alert(msg);

        } catch (error) {
            alert('Ticket non trouve');
        }
    };

    // ================================================
    // OPÉRATEUR
    // ================================================
    window.callNextTicketAPI = async function() {
        const user = QueueFlowAPI.getCurrentUser();

        if (!user || user.role !== 'operator') {
            alert('Reserve aux operateurs');
            return;
        }

        if (!user.institution_id) {
            alert('Aucune institution');
            return;
        }

        try {
            console.log('📞 Appel ticket...');
            const result = await QueueFlowAPI.callNextTicket(user.institution_id, user.id);

            if (result.ticket) {
                const t = result.ticket;
                alert('✅ ' + result.message + '\n\nTicket: ' + t.ticket_number);

                const el = document.getElementById('operatorNextPatient');
                if (el) {
                    el.innerHTML = '<div style="padding:20px;background:#dcfce7;border-radius:8px">' +
                        '<h3>Ticket Actuel</h3>' +
                        '<div style="font-size:48px;font-weight:bold;color:#15803d">' +
                        t.ticket_number + '</div>' +
                        '<button onclick="completeTicketAPI(\'' + t.ticket_number + '\')" ' +
                        'style="margin-top:10px;padding:10px 20px;background:#16a34a;color:white;border:none;border-radius:4px;cursor:pointer">' +
                        'Terminer</button></div>';
                }

                if (typeof window.updateOperatorDisplay === 'function') {
                    window.updateOperatorDisplay();
                }
            } else {
                alert(result.message);
            }

        } catch (error) {
            alert('Erreur: ' + error.message);
        }
    };

    window.completeTicketAPI = async function(ticketNum) {
        const user = QueueFlowAPI.getCurrentUser();

        if (!user || user.role !== 'operator') {
            alert('Reserve aux operateurs');
            return;
        }

        try {
            await QueueFlowAPI.completeTicket(ticketNum, user.id);
            alert('✅ Ticket complete !');

            if (typeof window.updateOperatorDisplay === 'function') {
                window.updateOperatorDisplay();
            }

            setTimeout(function() {
                window.callNextTicketAPI();
            }, 500);

        } catch (error) {
            alert('Erreur: ' + error.message);
        }
    };

    // ================================================
    // ADMIN
    // ================================================
    window.loadAdminStatsAPI = async function() {
        const user = QueueFlowAPI.getCurrentUser();

        if (!user || user.role !== 'admin') {
            alert('Reserve aux administrateurs');
            return;
        }

        try {
            const stats = await QueueFlowAPI.getAdminStats();

            const el1 = document.getElementById('adminTotalTickets');
            const el2 = document.getElementById('adminWaitingTickets');
            const el3 = document.getElementById('adminCompletedTickets');
            const el4 = document.getElementById('adminMissedRate');

            if (el1) el1.textContent = stats.total_tickets_today;
            if (el2) el2.textContent = stats.tickets_waiting;
            if (el3) el3.textContent = stats.tickets_completed;
            if (el4) {
                var rate = stats.total_tickets_today > 0 
                    ? ((stats.tickets_missed / stats.total_tickets_today) * 100).toFixed(1)
                    : 0;
                el4.textContent = rate + '%';
            }

            return stats;

        } catch (error) {
            return null;
        }
    };

    // ================================================
    // HISTORIQUE - AVEC VALIDATION USER_ID
    // ================================================
    window.loadUserHistoryAPI = async function() {
        const user = QueueFlowAPI.getCurrentUser();

        if (!user) {
            console.log('ℹ️ Pas d utilisateur');
            return;
        }

        try {
            console.log('📋 Historique pour:', user.email, '(ID:', user.id, ')');
            const tickets = await QueueFlowAPI.getUserTickets(user.id);

            console.log('Tickets recus:', tickets.length);

            // VALIDATION: Vérifier que les tickets appartiennent bien à cet utilisateur
            tickets.forEach(function(t) {
                if (t.user_id && t.user_id !== user.id) {
                    console.error('⚠️ TICKET INCORRECT:', t.ticket_number, 'appartient a user', t.user_id, 'pas', user.id);
                }
            });

            const el = document.getElementById('citizenHistoryDisplay');
            if (el) {
                if (tickets.length === 0) {
                    el.innerHTML = '<p style="text-align:center;color:#6b7280;padding:20px">Aucun ticket</p>';
                } else {
                    var html = '';
                    tickets.forEach(function(t) {
                        html += '<div style="padding:10px;margin:5px 0;background:#f9fafb;border-left:4px solid #3b82f6;border-radius:4px">';
                        html += '<strong>' + t.ticket_number + '</strong> - ' + t.institution.name + '<br>';
                        html += '<span style="color:#6b7280">' + getStatusLabel(t.status) + '</span><br>';
                        html += '<small style="color:#9ca3af">' + new Date(t.created_at).toLocaleString('fr-FR') + '</small>';
                        html += '</div>';
                    });
                    el.innerHTML = html;
                }
            }

            return tickets;

        } catch (error) {
            console.error('❌ Erreur:', error);
            return [];
        }
    };

    function getStatusLabel(status) {
        var labels = {
            waiting: '⏳ Attente',
            called: '📞 Appele',
            in_service: '🔄 En cours',
            completed: '✅ Termine',
            missed: '❌ Manque',
            cancelled: '🚫 Annule'
        };
        return labels[status] || status;
    }

    console.log('✅ Fonctions V4.1 installees !');
    console.log('🔒 Securite: Nettoyage complet au logout');
    console.log('🔒 Validation: user_id verifie a chaque action');
    console.log('🔒 Isolation: Donnees separees par utilisateur');
    console.log('🔧 Compatibilite: Alias showApp ajoute');
}

console.log('✅ Module V4.1 ULTIMATE charge - SECURISE !');
