/**
 * api-connector.js - Connecteur API pour QueueFlow
 * ================================================
 * Ce fichier connecte votre frontend QueueFlow.html au backend FastAPI
 * 
 * UTILISATION :
 * Ajoutez cette ligne dans votre HTML avant le script principal :
 * <script src="api-connector.js"></script>
 */

// ========================================
// CONFIGURATION DE L'API
// ========================================

const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        // Auth
        SIGNUP: '/auth/signup',
        LOGIN: '/auth/login',
        ME: '/auth/me',

        // Institutions
        INSTITUTIONS: '/institutions',
        INSTITUTIONS_BY_TYPE: '/institutions/type',

        // Tickets
        TICKETS: '/tickets',
        TICKET_STATS: '/tickets/:number/stats',
        USER_TICKETS: '/users/:userId/tickets',

        // Operator
        NEXT_TICKET: '/operator/next-ticket',
        COMPLETE_TICKET: '/operator/complete-ticket',
        MISS_TICKET: '/operator/miss-ticket',
        OPERATOR_STATS: '/operator/:operatorId/stats',

        // Admin
        ADMIN_STATS: '/admin/stats',
        ADMIN_OPERATORS: '/admin/operators',

        // Queue
        QUEUE_INFO: '/queue/:institutionId'
    }
};

// ========================================
// GESTION DE L'UTILISATEUR CONNECTÉ
// ========================================

/**
 * Récupère l'utilisateur connecté depuis localStorage
 */
function getCurrentUser() {
    const userJson = localStorage.getItem('currentUser');
    return userJson ? JSON.parse(userJson) : null;
}

/**
 * Sauvegarde l'utilisateur connecté dans localStorage
 */
function setCurrentUser(user) {
    if (user) {
        localStorage.setItem('currentUser', JSON.stringify(user));
    } else {
        localStorage.removeItem('currentUser');
    }
}

/**
 * Vérifie si un utilisateur est connecté
 */
function isLoggedIn() {
    return getCurrentUser() !== null;
}

// ========================================
// FONCTIONS UTILITAIRES
// ========================================

/**
 * Effectue une requête HTTP vers l'API
 */
async function apiRequest(endpoint, options = {}) {
    const url = API_CONFIG.BASE_URL + endpoint;

    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Erreur HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

/**
 * Remplace les paramètres dans l'URL
 * Exemple: replaceParams('/users/:id/tickets', {id: 5}) => '/users/5/tickets'
 */
function replaceParams(endpoint, params) {
    let url = endpoint;
    for (const [key, value] of Object.entries(params)) {
        url = url.replace(`:${key}`, value);
    }
    return url;
}

// ========================================
// FONCTIONS D'AUTHENTIFICATION
// ========================================

/**
 * Créer un nouveau compte utilisateur
 * 
 * @param {Object} userData - Données utilisateur
 * @param {string} userData.name - Nom complet
 * @param {string} userData.email - Email
 * @param {string} userData.password - Mot de passe
 * @param {string} userData.role - Rôle (citizen/operator/admin)
 * @returns {Promise<Object>} Utilisateur créé
 */
async function signup(userData) {
    const data = await apiRequest(API_CONFIG.ENDPOINTS.SIGNUP, {
        method: 'POST',
        body: JSON.stringify({
            name: userData.name,
            email: userData.email,
            password: userData.password,
            role: userData.role || 'citizen',
            institution_id: userData.institution_id || null
        })
    });

    // Connecter automatiquement après inscription
    setCurrentUser(data);
    return data;
}

/**
 * Se connecter avec email et mot de passe
 * 
 * @param {string} email - Email
 * @param {string} password - Mot de passe
 * @returns {Promise<Object>} Utilisateur connecté
 */
async function login(email, password) {
    const data = await apiRequest(API_CONFIG.ENDPOINTS.LOGIN, {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });

    setCurrentUser(data);
    return data;
}

/**
 * Se déconnecter
 */
function logout() {
    setCurrentUser(null);
    // Rediriger vers la page de login si nécessaire
    if (typeof renderApp === 'function') {
        renderApp();
    }
}

/**
 * Récupérer les infos de l'utilisateur connecté depuis le backend
 */
async function getMe(userId) {
    const endpoint = `${API_CONFIG.ENDPOINTS.ME}?user_id=${userId}`;
    return await apiRequest(endpoint);
}

// ========================================
// FONCTIONS POUR LES INSTITUTIONS
// ========================================

/**
 * Récupère toutes les institutions
 */
async function getAllInstitutions() {
    return await apiRequest(API_CONFIG.ENDPOINTS.INSTITUTIONS);
}

/**
 * Récupère les institutions par type
 * 
 * @param {string} type - Type d'institution (hospital/mairie/banque/transport)
 */
async function getInstitutionsByType(type) {
    const endpoint = `${API_CONFIG.ENDPOINTS.INSTITUTIONS_BY_TYPE}/${type}`;
    return await apiRequest(endpoint);
}

/**
 * Récupère une institution par ID
 */
async function getInstitutionById(id) {
    return await apiRequest(`${API_CONFIG.ENDPOINTS.INSTITUTIONS}/${id}`);
}

/**
 * Remplace la fonction populateInstitutions() du frontend
 * Charge les institutions depuis l'API au lieu des données statiques
 */
async function loadInstitutionsFromAPI() {
    try {
        const institutions = await getAllInstitutions();

        // Transformer en format attendu par le frontend
        const institutionsMap = {
            hospital: [],
            mairie: [],
            banque: [],
            transport: []
        };

        institutions.forEach(inst => {
            if (institutionsMap[inst.type]) {
                institutionsMap[inst.type].push({
                    id: inst.id,
                    name: inst.name,
                    location: inst.location,
                    address: inst.address,
                    phone: inst.phone
                });
            }
        });

        return institutionsMap;
    } catch (error) {
        console.error('Erreur chargement institutions:', error);
        return { hospital: [], mairie: [], banque: [], transport: [] };
    }
}

// ========================================
// FONCTIONS POUR LES TICKETS
// ========================================

/**
 * Créer un nouveau ticket
 * 
 * @param {number} institutionId - ID de l'institution
 * @param {number} userId - ID de l'utilisateur (optionnel)
 * @returns {Promise<Object>} Statistiques du ticket créé
 */
async function createTicket(institutionId, userId = null) {
    const data = await apiRequest(API_CONFIG.ENDPOINTS.TICKETS, {
        method: 'POST',
        body: JSON.stringify({
            institution_id: institutionId,
            user_id: userId
        })
    });

    return data;
}

/**
 * Vérifier les statistiques d'un ticket
 * 
 * @param {string} ticketNumber - Numéro du ticket (ex: H001)
 */
async function getTicketStats(ticketNumber) {
    const endpoint = replaceParams(API_CONFIG.ENDPOINTS.TICKET_STATS, { number: ticketNumber });
    return await apiRequest(endpoint);
}

/**
 * Récupérer l'historique des tickets d'un utilisateur
 */
async function getUserTickets(userId) {
    const endpoint = replaceParams(API_CONFIG.ENDPOINTS.USER_TICKETS, { userId });
    return await apiRequest(endpoint);
}

/**
 * Récupérer les informations complètes d'un ticket
 */
async function getTicketInfo(ticketNumber) {
    return await apiRequest(`${API_CONFIG.ENDPOINTS.TICKETS}/${ticketNumber}`);
}

// ========================================
// FONCTIONS POUR LES OPÉRATEURS
// ========================================

/**
 * Appeler le prochain ticket en attente
 * 
 * @param {number} institutionId - ID de l'institution
 * @param {number} operatorId - ID de l'opérateur
 */
async function callNextTicket(institutionId, operatorId) {
    const endpoint = `${API_CONFIG.ENDPOINTS.NEXT_TICKET}?institution_id=${institutionId}&operator_id=${operatorId}`;
    return await apiRequest(endpoint, { method: 'POST' });
}

/**
 * Marquer un ticket comme complété
 * 
 * @param {string} ticketNumber - Numéro du ticket
 * @param {number} operatorId - ID de l'opérateur
 */
async function completeTicket(ticketNumber, operatorId) {
    const endpoint = `${API_CONFIG.ENDPOINTS.COMPLETE_TICKET}/${ticketNumber}?operator_id=${operatorId}`;
    return await apiRequest(endpoint, { method: 'PUT' });
}

/**
 * Marquer un ticket comme manqué
 */
async function missTicket(ticketNumber) {
    const endpoint = `${API_CONFIG.ENDPOINTS.MISS_TICKET}/${ticketNumber}`;
    return await apiRequest(endpoint, { method: 'PUT' });
}

/**
 * Récupérer les statistiques d'un opérateur
 */
async function getOperatorStats(operatorId) {
    const endpoint = replaceParams(API_CONFIG.ENDPOINTS.OPERATOR_STATS, { operatorId });
    return await apiRequest(endpoint);
}

// ========================================
// FONCTIONS POUR LES ADMINISTRATEURS
// ========================================

/**
 * Récupérer les statistiques globales du système
 */
async function getAdminStats() {
    return await apiRequest(API_CONFIG.ENDPOINTS.ADMIN_STATS);
}

/**
 * Récupérer la liste de tous les opérateurs
 */
async function getAllOperators() {
    return await apiRequest(API_CONFIG.ENDPOINTS.ADMIN_OPERATORS);
}

// ========================================
// FONCTIONS POUR LES FILES D'ATTENTE
// ========================================

/**
 * Récupérer les informations de la file d'attente d'une institution
 */
async function getQueueInfo(institutionId) {
    const endpoint = replaceParams(API_CONFIG.ENDPOINTS.QUEUE_INFO, { institutionId });
    return await apiRequest(endpoint);
}

// ========================================
// FONCTIONS DE REMPLACEMENT POUR LE FRONTEND
// ========================================

/**
 * Remplace la fonction initializeUsers() du frontend
 * Les utilisateurs sont maintenant gérés par le backend
 */
function initializeUsersFromBackend() {
    // Les utilisateurs sont créés via signup
    // Charger l'utilisateur connecté depuis localStorage
    const currentUser = getCurrentUser();

    if (currentUser) {
        console.log('Utilisateur connecté:', currentUser.name, `(${currentUser.role})`);
    } else {
        console.log('Aucun utilisateur connecté');
    }
}

/**
 * Remplace la fonction generateMockTickets()
 * Les tickets sont maintenant créés via l'API
 */
async function loadTicketsFromBackend(userId) {
    if (!userId) return [];

    try {
        return await getUserTickets(userId);
    } catch (error) {
        console.error('Erreur chargement tickets:', error);
        return [];
    }
}

// ========================================
// EXPORT DES FONCTIONS (pour utilisation globale)
// ========================================

// Rendre les fonctions disponibles globalement
window.QueueFlowAPI = {
    // Config
    config: API_CONFIG,

    // Auth
    signup,
    login,
    logout,
    getCurrentUser,
    isLoggedIn,

    // Institutions
    getAllInstitutions,
    getInstitutionsByType,
    getInstitutionById,
    loadInstitutionsFromAPI,

    // Tickets
    createTicket,
    getTicketStats,
    getUserTickets,
    getTicketInfo,

    // Operator
    callNextTicket,
    completeTicket,
    missTicket,
    getOperatorStats,

    // Admin
    getAdminStats,
    getAllOperators,

    // Queue
    getQueueInfo,

    // Helpers
    initializeUsersFromBackend,
    loadTicketsFromBackend
};

console.log('✅ QueueFlow API Connector chargé');
console.log('📖 Utilisez window.QueueFlowAPI pour accéder aux fonctions');
console.log('🔗 API Backend:', API_CONFIG.BASE_URL);
