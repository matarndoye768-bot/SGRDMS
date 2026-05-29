"""
seed_db.py
Remplit la base de données avec des données de test réalistes.
Commande : python seed_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join("database", "sgrdms.db")

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print("🌱 Remplissage de la base de données...")

    # ----------------------------------------------------------
    # 1. SERVICES
    # ----------------------------------------------------------
    services = [
        ("Pédiatrie",       "Soins des enfants",              "Bâtiment A - RDC"),
        ("Généraliste",     "Médecine générale",              "Bâtiment B - 1er étage"),
        ("Gynécologie",     "Santé de la femme",              "Bâtiment A - 2ème étage"),
        ("Urgences",        "Prise en charge immédiate",      "Bâtiment C - RDC"),
        ("Pharmacie",       "Délivrance des médicaments",     "Bâtiment B - RDC"),
    ]
    cur.executemany(
        "INSERT INTO SERVICE (nom_service, description, localisation) VALUES (?,?,?)",
        services
    )
    print("  ✅ Services insérés")

    # ----------------------------------------------------------
    # 2. PATIENTS
    # ----------------------------------------------------------
    patients = [
        ("Amadou",   "Diallo",   "1990-03-15", "M", "Thiès - Médina",        "771234567"),
        ("Fatou",    "Ndiaye",   "1985-07-22", "F", "Thiès - Mbour",         "772345678"),
        ("Ibrahima", "Sow",      "2010-01-10", "M", "Thiès - Tivaoune",      "773456789"),
        ("Mariama",  "Ba",       "1995-11-30", "F", "Thiès - Fandène",       "774567890"),
        ("Ousmane",  "Fall",     "1978-05-05", "M", "Thiès - Ville",         "775678901"),
        ("Aissatou", "Diop",     "2000-09-18", "F", "Thiès - Keur Mousseu",  "776789012"),
        ("Cheikh",   "Mbaye",    "1965-12-01", "M", "Thiès - Nguinth",       "777890123"),
        ("Rokhaya",  "Cissé",    "1999-04-25", "F", "Thiès - Sambe",         "778901234"),
    ]
    cur.executemany(
        """INSERT INTO PATIENT (prenom, nom, date_naissance, sexe, adresse, telephone)
           VALUES (?,?,?,?,?,?)""",
        patients
    )
    print("  ✅ Patients insérés")

    # ----------------------------------------------------------
    # 3. MEDECINS
    # ----------------------------------------------------------
    medecins = [
        ("Docteur Moussa",   "Sarr",    "Pédiatre",      "msarr@tropical.sn",    "781111111", 1, 1),
        ("Docteur Aminata",  "Gueye",   "Généraliste",   "agueye@tropical.sn",   "782222222", 1, 2),
        ("Docteur Fatimata", "Diouf",   "Gynécologue",   "fdiouf@tropical.sn",   "783333333", 0, 3),
        ("Docteur Alioune",  "Faye",    "Urgentiste",    "afaye@tropical.sn",    "784444444", 0, 4),
        ("Docteur Seydou",   "Niang",   "Généraliste",   "sniang@tropical.sn",   "785555555", 1, 2),
    ]
    cur.executemany(
        """INSERT INTO MEDECIN (prenom, nom, specialite, email, telephone, telecons_active, id_service)
           VALUES (?,?,?,?,?,?,?)""",
        medecins
    )
    print("  ✅ Médecins insérés")

    # ----------------------------------------------------------
    # 4. DOSSIERS
    # ----------------------------------------------------------
    dossiers = [
        ("Paludisme chronique",  "2024-01-10", "Pénicilline",   "A+",  "actif", 1),
        ("Hypertension",         "2023-06-15", "Aucune",        "O+",  "actif", 2),
        ("Asthme",               "2022-03-20", "Aspirine",      "B+",  "actif", 3),
        ("Diabète type 2",       "2023-11-05", "Aucune",        "AB+", "actif", 4),
        ("Aucune",               "2024-02-28", "Arachides",     "A-",  "actif", 5),
        ("Anémie",               "2024-03-01", "Aucune",        "O-",  "actif", 6),
        ("Arthrose",             "2021-07-14", "Ibuprofène",    "B-",  "actif", 7),
        ("Aucune",               "2024-04-10", "Lactose",       "A+",  "actif", 8),
    ]
    cur.executemany(
        """INSERT INTO DOSSIER (maladie, date_creation, allergies, groupe_sanguin, status, id_patient)
           VALUES (?,?,?,?,?,?)""",
        dossiers
    )
    print("  ✅ Dossiers insérés")

    # ----------------------------------------------------------
    # 5. RENDEZ_VOUS
    # ----------------------------------------------------------
    rdvs = [
        ("2026-05-20 08:00", "Fièvre persistante",     "termine",    "presentiel",       1, 1),
        ("2026-05-21 09:30", "Contrôle tension",       "termine",    "presentiel",       2, 2),
        ("2026-05-22 10:00", "Toux chronique",         "termine",    "presentiel",       3, 1),
        ("2026-05-23 11:00", "Consultation diabète",   "termine",    "presentiel",       4, 2),
        ("2026-05-27 08:30", "Mal de tête",            "confirme",   "presentiel",       5, 2),
        ("2026-05-27 09:00", "Suivi grossesse",        "confirme",   "presentiel",       6, 3),
        ("2026-05-28 10:30", "Douleurs articulaires",  "en_attente", "presentiel",       7, 5),
        ("2026-05-28 14:00", "Consultation générale",  "en_attente", "teleconsultation", 8, 5),
        ("2026-05-20 15:00", "Contrôle asthme",        "annule",     "presentiel",       3, 2),
        ("2026-05-29 08:00", "Renouvellement ordo",    "en_attente", "presentiel",       1, 2),
    ]
    cur.executemany(
        """INSERT INTO RENDEZ_VOUS (date_heure, motif, statut, type, id_patient, id_medecin)
           VALUES (?,?,?,?,?,?)""",
        rdvs
    )
    print("  ✅ Rendez-vous insérés")

    # ----------------------------------------------------------
    # 6. TELECONSULTATION (pour le RDV 8 - teleconsultation)
    # ----------------------------------------------------------
    teleconsultations = [
        ("https://meet.tropical.sn/session-abc123", "planifie", 30, "2026-05-28 14:00", 8),
    ]
    cur.executemany(
        """INSERT INTO TELECONSULTATION (lien_video, statut, duree, date_heure, id_rdv)
           VALUES (?,?,?,?,?)""",
        teleconsultations
    )
    print("  ✅ Téléconsultations insérées")

    # ----------------------------------------------------------
    # 7. CONSULTATIONS (pour les RDV terminés : 1,2,3,4)
    # ----------------------------------------------------------
    consultations = [
        ("2026-05-20", "Fièvre persistante",   "Paludisme",          "Repos recommandé",   68.0, 38.5, "110/70", 1),
        ("2026-05-21", "Contrôle tension",     "Hypertension stable","Continuer traitement",72.0, 37.0, "140/90", 2),
        ("2026-05-22", "Toux chronique",       "Bronchite aiguë",    "Antibiotiques 7j",    25.0, 37.2, "100/65", 3),
        ("2026-05-23", "Consultation diabète", "Diabète contrôlé",   "Régime strict",       85.0, 36.8, "120/80", 4),
    ]
    cur.executemany(
        """INSERT INTO CONSULTATION
           (date_consultation, motif, diagnostic, note, poids, temperature, tension, id_rdv)
           VALUES (?,?,?,?,?,?,?,?)""",
        consultations
    )
    print("  ✅ Consultations insérées")

    # ----------------------------------------------------------
    # 8. MEDICAMENTS
    # ----------------------------------------------------------
    medicaments = [
        ("Paracétamol",    "500mg",  "Antidouleur et antipyrétique",         "2027-12-31"),
        ("Amoxicilline",   "250mg",  "Antibiotique à large spectre",         "2026-08-15"),
        ("Metformine",     "500mg",  "Antidiabétique oral",                  "2027-06-30"),
        ("Amlodipine",     "5mg",    "Antihypertenseur",                     "2027-03-20"),
        ("Salbutamol",     "100mcg", "Bronchodilatateur - spray asthme",     "2026-11-10"),
        ("Artéméther",     "20mg",   "Antipaludéen",                         "2026-09-01"),
        ("Ibuprofène",     "400mg",  "Anti-inflammatoire",                   "2027-01-15"),
        ("Oméprazole",     "20mg",   "Protecteur gastrique",                 "2027-05-20"),
    ]
    cur.executemany(
        """INSERT INTO MEDICAMENT (nom, dosage, description, date_expiration)
           VALUES (?,?,?,?)""",
        medicaments
    )
    print("  ✅ Médicaments insérés")

    # ----------------------------------------------------------
    # 9. ORDONNANCES (pour les consultations 1,2,3,4)
    # ----------------------------------------------------------
    ordonnances = [
        ("active", "2026-05-20", "Prendre avec de l'eau. Repos 3 jours.",     1),
        ("active", "2026-05-21", "Continuer le traitement sans interruption.", 2),
        ("active", "2026-05-22", "Terminer le traitement antibiotique.",       3),
        ("active", "2026-05-23", "Régime pauvre en sucre. Contrôle mensuel.", 4),
    ]
    cur.executemany(
        """INSERT INTO ORDONNANCE (statut, date, instruction, id_consultation)
           VALUES (?,?,?,?)""",
        ordonnances
    )
    print("  ✅ Ordonnances insérées")

    # ----------------------------------------------------------
    # 10. LIGNES D'ORDONNANCE
    # ----------------------------------------------------------
    lignes = [
        # Ordonnance 1 - Paludisme (Artéméther + Paracétamol)
        ("2 fois/jour", "3 jours",  6,  "orale", 1, 6),
        ("3 fois/jour", "5 jours",  15, "orale", 1, 1),
        # Ordonnance 2 - Hypertension (Amlodipine)
        ("1 fois/jour", "30 jours", 30, "orale", 2, 4),
        # Ordonnance 3 - Bronchite (Amoxicilline + Ibuprofène)
        ("3 fois/jour", "7 jours",  21, "orale", 3, 2),
        ("2 fois/jour", "5 jours",  10, "orale", 3, 7),
        # Ordonnance 4 - Diabète (Metformine + Oméprazole)
        ("2 fois/jour", "30 jours", 60, "orale", 4, 3),
        ("1 fois/jour", "30 jours", 30, "orale", 4, 8),
    ]
    cur.executemany(
        """INSERT INTO LIGNE_ORDONNANCE
           (frequence, duree_traitement, quantite, voie_administration, id_ordonnance, id_medicament)
           VALUES (?,?,?,?,?,?)""",
        lignes
    )
    print("  ✅ Lignes d'ordonnance insérées")

    # ----------------------------------------------------------
    # 11. ASSURANCES
    # ----------------------------------------------------------
    assurances = [
        ("CNSS Sénégal",  "CNSS-2024-001", 80.0, 500000.0, "2024-01-01", "2026-12-31", 2),
        ("Allianz",       "ALZ-2023-445",  70.0, 300000.0, "2023-06-01", "2026-05-31", 4),
        ("Sanlam",        "SAN-2024-789",  60.0, 200000.0, "2024-03-01", "2027-02-28", 6),
    ]
    cur.executemany(
        """INSERT INTO ASSURANCE
           (nom_assureur, numero_contrat, taux_couverture, plafond_annuel, date_debut, date_fin, id_patient)
           VALUES (?,?,?,?,?,?,?)""",
        assurances
    )
    print("  ✅ Assurances insérées")

    # ----------------------------------------------------------
    # 12. FACTURES
    # ----------------------------------------------------------
    factures = [
        ("2026-05-20", 15000.0, "especes",  "FAC-2026-001", 1),
        ("2026-05-21", 10000.0, "assurance","FAC-2026-002", 2),
        ("2026-05-22", 20000.0, "especes",  "FAC-2026-003", 3),
        ("2026-05-23", 12000.0, "carte",    "FAC-2026-004", 4),
    ]
    cur.executemany(
        """INSERT INTO FACTURE (date_facturation, montant_total, mode_paiement, num_facture, id_patient)
           VALUES (?,?,?,?,?)""",
        factures
    )
    print("  ✅ Factures insérées")

    # ----------------------------------------------------------
    # 13. PAIEMENTS
    # ----------------------------------------------------------
    paiements = [
        ("2026-05-20", 15000.0, "especes",   "paye",      "direct",    1),
        ("2026-05-21",  2000.0, "assurance", "paye",      "assurance", 2),
        ("2026-05-22", 20000.0, "especes",   "paye",      "direct",    3),
        ("2026-05-23", 12000.0, "carte",     "paye",      "direct",    4),
    ]
    cur.executemany(
        """INSERT INTO PAIEMENT
           (date_paiement, montant, mode_paiement, statut_paiement, type_paiement, id_facture)
           VALUES (?,?,?,?,?,?)""",
        paiements
    )
    print("  ✅ Paiements insérés")

    # ----------------------------------------------------------
    # 14. NOTIFICATIONS
    # ----------------------------------------------------------
    notifications = [
        ("Votre RDV du 27/05 à 08h30 est confirmé.",              0, "non_lu", 5),
        ("Votre RDV du 27/05 à 09h00 est confirmé.",              0, "non_lu", 6),
        ("Rappel : RDV demain 28/05 à 10h30.",                    0, "non_lu", 7),
        ("Votre ordonnance du 20/05 est disponible.",             1, "lu",     1),
        ("Facture FAC-2026-002 réglée par votre assurance CNSS.", 1, "lu",     2),
        ("Votre RDV du 20/05 a été annulé. Reprogrammez svp.",    1, "lu",     3),
    ]
    cur.executemany(
        """INSERT INTO NOTIFICATION (contenu, lu, statut, id_patient)
           VALUES (?,?,?,?)""",
        notifications
    )
    print("  ✅ Notifications insérées")

    # ----------------------------------------------------------
    # 15. LISTE D'ATTENTE
    # ----------------------------------------------------------
    listes = [
        ("2026-05-27", 1, "en_attente", "urgent",  5),
        ("2026-05-27", 2, "en_attente", "normal",  6),
        ("2026-05-27", 3, "en_attente", "normal",  8),
    ]
    cur.executemany(
        """INSERT INTO LISTE_ATTENTE
           (date_inscription, position, statut, niveau_priorite, id_patient)
           VALUES (?,?,?,?,?)""",
        listes
    )

    # ----------------------------------------------------------
    # 16. LISTE_ATTENTE_PATIENT
    # ----------------------------------------------------------
    lap = [(5, 1), (6, 2), (8, 3)]
    cur.executemany(
        "INSERT INTO LISTE_ATTENTE_PATIENT (id_patient, id_liste) VALUES (?,?)",
        lap
    )
    print("  ✅ Listes d'attente insérées")

    # ----------------------------------------------------------
    # COMMIT
    # ----------------------------------------------------------
    conn.commit()
    conn.close()

    print("\n🎉 Base de données remplie avec succès !")
    print("📊 Résumé :")
    print("   - 5  services")
    print("   - 8  patients")
    print("   - 5  médecins")
    print("   - 8  dossiers")
    print("   - 10 rendez-vous")
    print("   - 4  consultations")
    print("   - 1  téléconsultation")
    print("   - 4  ordonnances + 7 lignes")
    print("   - 8  médicaments")
    print("   - 3  assurances")
    print("   - 4  factures + 4 paiements")
    print("   - 6  notifications")
    print("   - 3  listes d'attente")

if __name__ == "__main__":
    seed()
