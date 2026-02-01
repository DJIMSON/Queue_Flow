#!/usr/bin/env python3
"""
QueueFlow Backend - Script de Lancement
Avec création automatique des utilisateurs par défaut
"""
import uvicorn
from database import engine, Base, SessionLocal
from models import User, Institution, Ticket

def create_default_users():
    """Créer les utilisateurs par défaut : Admin + 12 Opérateurs"""
    from crud_users import create_user
    from schemas import UserCreate

    db = SessionLocal()

    try:
        print('\n' + '='*60)
        print('👥 CRÉATION DES UTILISATEURS PAR DÉFAUT')
        print('='*60)

        # 1. ADMIN
        existing_admin = db.query(User).filter(User.email == 'admin@queueflow.sn').first()
        if existing_admin:
            print('✅ Admin existe déjà')
        else:
            admin_data = UserCreate(
                email='admin@queueflow.sn',
                password='admin123',
                name='Admin QueueFlow',
                role='admin',
                institution_id=None
            )
            create_user(db, admin_data)
            print('✅ Admin créé (admin@queueflow.sn / admin123)')

        # 2. OPÉRATEURS (1 par institution)
        operators = [
            (1, 'Hôpital Aristide Le Dantec', 'operator@ledantec.sn'),
            (2, 'Hôpital Principal de Dakar', 'operator@principal.sn'),
            (3, 'Hôpital Fann', 'operator@fann.sn'),
            (4, 'Hôpital Abass Ndao', 'operator@abassndao.sn'),
            (5, 'Clinique Cheikh Zaid', 'operator@cheikh.sn'),
            (6, 'Mairie Plateau', 'operator@plateau.sn'),
            (7, 'Mairie Medina', 'operator@medina.sn'),
            (8, 'Mairie Parcelles Assainies', 'operator@parcelles.sn'),
            (9, 'Banque BICIS', 'operator@bicis.sn'),
            (10, 'SGBS Société Générale', 'operator@sgbs.sn'),
            (11, 'BOA Sénégal', 'operator@boa.sn'),
            (12, 'Centre DAKAR-BUS', 'operator@dakarbus.sn'),
        ]

        created_count = 0
        for inst_id, inst_name, email in operators:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f'✅ Opérateur {inst_name} existe déjà')
            else:
                operator_data = UserCreate(
                    email=email,
                    password='operator123',
                    name=f'Opérateur {inst_name}',
                    role='operator',
                    institution_id=inst_id
                )
                create_user(db, operator_data)
                print(f'✅ Opérateur créé pour {inst_name} ({email})')
                created_count += 1

        print('\n' + '='*60)
        if created_count > 0:
            print(f'🎉 {created_count} NOUVEAUX OPÉRATEURS CRÉÉS !')
        print('📋 COMPTES DISPONIBLES :')
        print('='*60)
        print('👔 ADMIN     : admin@queueflow.sn / admin123')
        print('👨‍💼 OPÉRATEURS: operator@[institution].sn / operator123')
        print('   Exemples : operator@ledantec.sn, operator@plateau.sn')
        print('='*60 + '\n')

    except Exception as e:
        print(f'❌ Erreur création utilisateurs: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    print('='*60)
    print('🚀 QUEUEFLOW BACKEND - DÉMARRAGE')
    print('='*60)

    # Créer les tables
    print('\n📊 Création des tables de la base de données...')
    Base.metadata.create_all(bind=engine)
    print('✅ Tables créées avec succès')

    # Créer les utilisateurs par défaut
    create_default_users()

    # Démarrer le serveur
    print('\n' + '='*60)
    print('🌐 DÉMARRAGE DU SERVEUR API')
    print('='*60)
    print('📍 URL : http://localhost:8000')
    print('📖 Documentation : http://localhost:8000/docs')
    print('='*60 + '\n')

    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
        log_level='info'
    )
