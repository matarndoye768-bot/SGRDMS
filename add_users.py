"""
add_users.py
Ajoute les utilisateurs de test dans la base.
Commande : python add_users.py
"""

import sqlite3, hashlib, os

DB_PATH = os.path.join("database", "sgrdms.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# Création de la table si elle n'existe pas encore
cur.executescript("""
CREATE TABLE IF NOT EXISTS UTILISATEUR (
    id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
    login          TEXT    NOT NULL UNIQUE,
    mot_de_passe   TEXT    NOT NULL,
    role           TEXT    NOT NULL CHECK(role IN ('admin','medecin','accueil')),
    nom_complet    TEXT    NOT NULL,
    actif          INTEGER NOT NULL DEFAULT 1 CHECK(actif IN (0,1)),
    id_medecin     INTEGER DEFAULT NULL,
    FOREIGN KEY (id_medecin) REFERENCES MEDECIN(id_medecin)
);
""")

utilisateurs = [
    ("admin",    hash_password("admin123"),   "admin",   "Administrateur Système", 1, None),
    ("accueil",  hash_password("accueil123"), "accueil", "Secrétaire Accueil",     1, None),
    ("msarr",    hash_password("medecin123"), "medecin", "Dr. Moussa Sarr",        1, 1),
    ("agueye",   hash_password("medecin123"), "medecin", "Dr. Aminata Gueye",      1, 2),
    ("fdiouf",   hash_password("medecin123"), "medecin", "Dr. Fatimata Diouf",     1, 3),
]

cur.executemany("""
    INSERT OR IGNORE INTO UTILISATEUR
    (login, mot_de_passe, role, nom_complet, actif, id_medecin)
    VALUES (?,?,?,?,?,?)
""", utilisateurs)

conn.commit()
conn.close()

print("✅ Utilisateurs créés avec succès !")
print()
print("🔑 Comptes disponibles :")
print("   login: admin    | mot de passe: admin123")
print("   login: accueil  | mot de passe: accueil123")
print("   login: msarr    | mot de passe: medecin123")
print("   login: agueye   | mot de passe: medecin123")
print("   login: fdiouf   | mot de passe: medecin123")