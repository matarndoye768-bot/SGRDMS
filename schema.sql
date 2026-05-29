-- ============================================================
--   SGRDMS - Système de Gestion des Rendez-vous et Dossiers
--             Médicaux d'un Centre de Santé
--   Base de données : SQLite
--   Université Iba Der Thiam de Thiès - L2 Génie Logiciel
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. SERVICE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS SERVICE (
    id_service   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_service  TEXT    NOT NULL,
    description  TEXT,
    localisation TEXT
);

-- ------------------------------------------------------------
-- 2. PATIENT
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS PATIENT (
    id_patient     INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom         TEXT    NOT NULL,
    nom            TEXT    NOT NULL,
    date_naissance TEXT    NOT NULL,   -- format YYYY-MM-DD
    sexe           TEXT    NOT NULL CHECK(sexe IN ('M', 'F')),
    adresse        TEXT,
    telephone      TEXT
);

-- ------------------------------------------------------------
-- 3. MEDECIN
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS MEDECIN (
    id_medecin       INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom           TEXT    NOT NULL,
    nom              TEXT    NOT NULL,
    specialite       TEXT    NOT NULL,
    email            TEXT    UNIQUE,
    telephone        TEXT,
    telecons_active  INTEGER NOT NULL DEFAULT 0 CHECK(telecons_active IN (0, 1)),
    id_service       INTEGER NOT NULL,
    FOREIGN KEY (id_service) REFERENCES SERVICE(id_service)
);

-- ------------------------------------------------------------
-- 4. DOSSIER
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DOSSIER (
    id_dossier     INTEGER PRIMARY KEY AUTOINCREMENT,
    maladie        TEXT,
    date_creation  TEXT    NOT NULL DEFAULT (DATE('now')),
    allergies      TEXT,
    groupe_sanguin TEXT,
    status         TEXT    NOT NULL DEFAULT 'actif',
    id_patient     INTEGER NOT NULL UNIQUE,   -- 1 dossier par patient
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient)
);

-- ------------------------------------------------------------
-- 5. RENDEZ_VOUS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS RENDEZ_VOUS (
    id_rdv      INTEGER PRIMARY KEY AUTOINCREMENT,
    date_heure  TEXT    NOT NULL,   -- format YYYY-MM-DD HH:MM
    motif       TEXT,
    statut      TEXT    NOT NULL DEFAULT 'en_attente'
                    CHECK(statut IN ('en_attente','confirme','annule','termine')),
    type        TEXT    NOT NULL DEFAULT 'presentiel'
                    CHECK(type IN ('presentiel','teleconsultation')),
    id_patient  INTEGER NOT NULL,
    id_medecin  INTEGER NOT NULL,
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient),
    FOREIGN KEY (id_medecin) REFERENCES MEDECIN(id_medecin)
);

-- ------------------------------------------------------------
-- 6. TELECONSULTATION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TELECONSULTATION (
    id_teleconsultation INTEGER PRIMARY KEY AUTOINCREMENT,
    lien_video          TEXT,
    statut              TEXT DEFAULT 'planifie'
                            CHECK(statut IN ('planifie','en_cours','termine')),
    duree               INTEGER,   -- en minutes
    date_heure          TEXT NOT NULL,
    id_rdv              INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (id_rdv) REFERENCES RENDEZ_VOUS(id_rdv)
);

-- ------------------------------------------------------------
-- 7. CONSULTATION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS CONSULTATION (
    id_consultation  INTEGER PRIMARY KEY AUTOINCREMENT,
    date_consultation TEXT   NOT NULL DEFAULT (DATE('now')),
    motif            TEXT,
    diagnostic       TEXT,
    note             TEXT,
    poids            REAL,          -- en kg
    temperature      REAL,          -- en °C
    tension          TEXT,          -- ex: "120/80"
    id_rdv           INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (id_rdv) REFERENCES RENDEZ_VOUS(id_rdv)
);

-- ------------------------------------------------------------
-- 8. ORDONNANCE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ORDONNANCE (
    id_ordonnance   INTEGER PRIMARY KEY AUTOINCREMENT,
    statut          TEXT DEFAULT 'active' CHECK(statut IN ('active','expiree','annulee')),
    date            TEXT NOT NULL DEFAULT (DATE('now')),
    instruction     TEXT,
    id_consultation INTEGER NOT NULL,
    FOREIGN KEY (id_consultation) REFERENCES CONSULTATION(id_consultation)
);

-- ------------------------------------------------------------
-- 9. MEDICAMENT
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS MEDICAMENT (
    id_medicament  INTEGER PRIMARY KEY AUTOINCREMENT,
    nom            TEXT NOT NULL,
    dosage         TEXT,
    description    TEXT,
    date_expiration TEXT
);

-- ------------------------------------------------------------
-- 10. LIGNE_ORDONNANCE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS LIGNE_ORDONNANCE (
    id_ligne           INTEGER PRIMARY KEY AUTOINCREMENT,
    frequence          TEXT,     -- ex: "3 fois/jour"
    duree_traitement   TEXT,     -- ex: "7 jours"
    quantite           INTEGER,
    voie_administration TEXT,   -- ex: "orale", "injectable"
    id_ordonnance      INTEGER NOT NULL,
    id_medicament      INTEGER NOT NULL,
    FOREIGN KEY (id_ordonnance) REFERENCES ORDONNANCE(id_ordonnance),
    FOREIGN KEY (id_medicament) REFERENCES MEDICAMENT(id_medicament)
);

-- ------------------------------------------------------------
-- 11. ASSURANCE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ASSURANCE (
    id_assurance    INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_assureur    TEXT    NOT NULL,
    numero_contrat  TEXT    UNIQUE,
    taux_couverture REAL    CHECK(taux_couverture BETWEEN 0 AND 100),
    plafond_annuel  REAL,
    date_debut      TEXT,
    date_fin        TEXT,
    id_patient      INTEGER NOT NULL,
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient)
);

-- ------------------------------------------------------------
-- 12. FACTURE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FACTURE (
    id_facture      INTEGER PRIMARY KEY AUTOINCREMENT,
    date_facturation TEXT   NOT NULL DEFAULT (DATE('now')),
    montant_total   REAL    NOT NULL,
    mode_paiement   TEXT,
    num_facture     TEXT    UNIQUE NOT NULL,
    id_patient      INTEGER NOT NULL,
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient)
);

-- ------------------------------------------------------------
-- 13. PAIEMENT
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS PAIEMENT (
    id_paiement     INTEGER PRIMARY KEY AUTOINCREMENT,
    date_paiement   TEXT    NOT NULL DEFAULT (DATE('now')),
    montant         REAL    NOT NULL,
    mode_paiement   TEXT,
    statut_paiement TEXT    DEFAULT 'en_attente'
                        CHECK(statut_paiement IN ('en_attente','paye','echec')),
    type_paiement   TEXT,   -- ex: "especes", "carte", "assurance"
    id_facture      INTEGER NOT NULL,
    FOREIGN KEY (id_facture) REFERENCES FACTURE(id_facture)
);

-- ------------------------------------------------------------
-- 14. NOTIFICATION
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS NOTIFICATION (
    id_notification INTEGER PRIMARY KEY AUTOINCREMENT,
    contenu         TEXT    NOT NULL,
    lu              INTEGER NOT NULL DEFAULT 0 CHECK(lu IN (0, 1)),
    statut          TEXT    DEFAULT 'non_lu' CHECK(statut IN ('non_lu','lu')),
    id_patient      INTEGER NOT NULL,
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient)
);

-- ------------------------------------------------------------
-- 15. LISTE_ATTENTE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS LISTE_ATTENTE (
    id_liste         INTEGER PRIMARY KEY AUTOINCREMENT,
    date_inscription TEXT    NOT NULL DEFAULT (DATE('now')),
    position         INTEGER,
    statut           TEXT    DEFAULT 'en_attente'
                         CHECK(statut IN ('en_attente','appele','annule')),
    niveau_priorite  TEXT    DEFAULT 'normal'
                         CHECK(niveau_priorite IN ('normal','urgent','critique')),
    id_patient       INTEGER NOT NULL,
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient)
);

-- ------------------------------------------------------------
-- 16. LISTE_ATTENTE_PATIENT  (table d'association)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS LISTE_ATTENTE_PATIENT (
    id_patient INTEGER NOT NULL,
    id_liste   INTEGER NOT NULL,
    PRIMARY KEY (id_patient, id_liste),
    FOREIGN KEY (id_patient) REFERENCES PATIENT(id_patient),
    FOREIGN KEY (id_liste)   REFERENCES LISTE_ATTENTE(id_liste)
);

-- ============================================================
-- FIN DU SCHEMA
-- ============================================================
