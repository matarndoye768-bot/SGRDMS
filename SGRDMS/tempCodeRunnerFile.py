"""
init_db.py
Lance ce script UNE SEULE FOIS pour créer la base de données.
Commande : python init_db.py
"""

import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join("database", "sgrdms.db")
SCHEMA_PATH = "schema.sql"

def init_db():
    # Crée le dossier database/ s'il n'existe pas
    os.makedirs("database", exist_ok=True)

    # Connexion à la base (la crée si elle n'existe pas)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lit et exécute le schéma SQL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    cursor.executescript(schema)
    conn.commit()
    conn.close()

    print("✅ Base de données créée avec succès !")
    print(f"📁 Fichier : {DB_PATH}")

if __name__ == "__main__":
    init_db()