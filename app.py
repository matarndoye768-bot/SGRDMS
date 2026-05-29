"""
app.py - Application principale SGRDMS
Lancement : python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, hashlib, os

app = Flask(__name__)
app.secret_key = "sgrdms_secret_key_2026"

DB_PATH = os.path.join("database", "sgrdms.db")

# Auto-initialisation de la base au démarrage
import hashlib

def hp(p): 
    return hashlib.sha256(p.encode()).hexdigest()

os.makedirs("database", exist_ok=True)

if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.execute("INSERT OR IGNORE INTO UTILISATEUR (login, mot_de_passe, role, nom_complet, actif) VALUES (?,?,?,?,1)", 
                ("admin", hp("admin123"), "admin", "Administrateur Système"))
    conn.execute("INSERT OR IGNORE INTO UTILISATEUR (login, mot_de_passe, role, nom_complet, actif) VALUES (?,?,?,?,1)", 
                ("accueil", hp("accueil123"), "accueil", "Secrétaire Accueil"))
    conn.execute("INSERT OR IGNORE INTO UTILISATEUR (login, mot_de_passe, role, nom_complet, actif) VALUES (?,?,?,?,1)", 
                ("msarr", hp("medecin123"), "medecin", "Dr. Moussa Sarr"))
    conn.commit()
    conn.close()

# ============================================================
# UTILITAIRES
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Accès non autorisé.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================================
# AUTH — LOGIN / LOGOUT
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        login_input = request.form.get("login", "").strip()
        password    = request.form.get("password", "").strip()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM UTILISATEUR WHERE login = ? AND mot_de_passe = ? AND actif = 1",
            (login_input, hash_password(password))
        ).fetchone()
        conn.close()

        if user:
            session["user"]       = user["login"]
            session["role"]       = user["role"]
            session["nom"]        = user["nom_complet"]
            session["id_medecin"] = user["id_medecin"]
            flash(f"Bienvenue, {user['nom_complet']} !", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Login ou mot de passe incorrect.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()

    stats = {
        "patients"     : conn.execute("SELECT COUNT(*) FROM PATIENT").fetchone()[0],
        "medecins"     : conn.execute("SELECT COUNT(*) FROM MEDECIN").fetchone()[0],
        "rdv_today"    : conn.execute(
            "SELECT COUNT(*) FROM RENDEZ_VOUS WHERE date_heure LIKE ? AND statut != 'annule'",
            (f"{__import__('datetime').date.today()}%",)
        ).fetchone()[0],
        "consultations": conn.execute("SELECT COUNT(*) FROM CONSULTATION").fetchone()[0],
        "factures"     : conn.execute("SELECT COUNT(*) FROM FACTURE").fetchone()[0],
        "en_attente"   : conn.execute(
            "SELECT COUNT(*) FROM LISTE_ATTENTE WHERE statut = 'en_attente'"
        ).fetchone()[0],
    }

    # Derniers RDV du jour
    rdv_today = conn.execute("""
        SELECT r.id_rdv, r.date_heure, r.motif, r.statut, r.type,
               p.prenom || ' ' || p.nom AS patient,
               m.prenom || ' ' || m.nom AS medecin
        FROM RENDEZ_VOUS r
        JOIN PATIENT p ON r.id_patient = p.id_patient
        JOIN MEDECIN m ON r.id_medecin = m.id_medecin
        ORDER BY r.date_heure DESC
        LIMIT 5
    """).fetchall()

    conn.close()
    return render_template("dashboard.html", stats=stats, rdv_today=rdv_today)


# ============================================================
# PATIENTS
# ============================================================

@app.route("/patients")
@login_required
def patients_liste():
    conn  = get_db()
    search = request.args.get("q", "")
    if search:
        patients = conn.execute(
            """SELECT * FROM PATIENT
               WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ?""",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        ).fetchall()
    else:
        patients = conn.execute("SELECT * FROM PATIENT ORDER BY nom").fetchall()
    conn.close()
    return render_template("patients/liste.html", patients=patients, search=search)


@app.route("/patients/nouveau", methods=["GET", "POST"])
@login_required
def patient_nouveau():
    if request.method == "POST":
        prenom         = request.form["prenom"]
        nom            = request.form["nom"]
        date_naissance = request.form["date_naissance"]
        sexe           = request.form["sexe"]
        adresse        = request.form.get("adresse", "")
        telephone      = request.form.get("telephone", "")

        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            """INSERT INTO PATIENT (prenom, nom, date_naissance, sexe, adresse, telephone)
               VALUES (?,?,?,?,?,?)""",
            (prenom, nom, date_naissance, sexe, adresse, telephone)
        )
        id_patient = cur.lastrowid

        # Créer automatiquement un dossier vide pour ce patient
        cur.execute(
            "INSERT INTO DOSSIER (id_patient) VALUES (?)",
            (id_patient,)
        )
        conn.commit()
        conn.close()
        flash(f"Patient {prenom} {nom} enregistré avec succès !", "success")
        return redirect(url_for("patients_liste"))

    return render_template("patients/nouveau.html")


@app.route("/patients/<int:id>")
@login_required
def patient_detail(id):
    conn    = get_db()
    patient = conn.execute("SELECT * FROM PATIENT WHERE id_patient = ?", (id,)).fetchone()
    dossier = conn.execute("SELECT * FROM DOSSIER WHERE id_patient = ?",  (id,)).fetchone()
    rdvs    = conn.execute(
        """SELECT r.*, m.prenom || ' ' || m.nom AS medecin
           FROM RENDEZ_VOUS r
           JOIN MEDECIN m ON r.id_medecin = m.id_medecin
           WHERE r.id_patient = ?
           ORDER BY r.date_heure DESC""", (id,)
    ).fetchall()
    conn.close()
    if not patient:
        flash("Patient introuvable.", "danger")
        return redirect(url_for("patients_liste"))
    return render_template("patients/detail.html", patient=patient, dossier=dossier, rdvs=rdvs)


# ============================================================
# MEDECINS
# ============================================================

@app.route("/medecins")
@login_required
def medecins_liste():
    conn     = get_db()
    medecins = conn.execute(
        """SELECT m.*, s.nom_service
           FROM MEDECIN m JOIN SERVICE s ON m.id_service = s.id_service
           ORDER BY m.nom"""
    ).fetchall()
    conn.close()
    return render_template("medecins/liste.html", medecins=medecins)


@app.route("/medecins/nouveau", methods=["GET", "POST"])
@login_required
@role_required("admin")
def medecin_nouveau():
    conn     = get_db()
    services = conn.execute("SELECT * FROM SERVICE").fetchall()

    if request.method == "POST":
        prenom          = request.form["prenom"]
        nom             = request.form["nom"]
        specialite      = request.form["specialite"]
        email           = request.form["email"]
        telephone       = request.form.get("telephone", "")
        telecons_active = 1 if request.form.get("telecons_active") else 0
        id_service      = request.form["id_service"]

        conn.execute(
            """INSERT INTO MEDECIN
               (prenom, nom, specialite, email, telephone, telecons_active, id_service)
               VALUES (?,?,?,?,?,?,?)""",
            (prenom, nom, specialite, email, telephone, telecons_active, id_service)
        )
        conn.commit()
        conn.close()
        flash(f"Médecin Dr. {prenom} {nom} ajouté avec succès !", "success")
        return redirect(url_for("medecins_liste"))

    conn.close()
    return render_template("medecins/nouveau.html", services=services)


# ============================================================
# SERVICES
# ============================================================

@app.route("/services")
@login_required
def services_liste():
    conn     = get_db()
    services = conn.execute("SELECT * FROM SERVICE ORDER BY nom_service").fetchall()
    conn.close()
    return render_template("services/liste.html", services=services)


@app.route("/services/nouveau", methods=["GET", "POST"])
@login_required
@role_required("admin")
def service_nouveau():
    if request.method == "POST":
        nom_service  = request.form["nom_service"]
        description  = request.form.get("description", "")
        localisation = request.form.get("localisation", "")

        conn = get_db()
        conn.execute(
            "INSERT INTO SERVICE (nom_service, description, localisation) VALUES (?,?,?)",
            (nom_service, description, localisation)
        )
        conn.commit()
        conn.close()
        flash(f"Service '{nom_service}' créé avec succès !", "success")
        return redirect(url_for("services_liste"))

    return render_template("services/nouveau.html")


# ============================================================
# RENDEZ-VOUS
# ============================================================

@app.route("/rdv")
@login_required
def rdv_liste():
    conn = get_db()
    rdvs = conn.execute("""
        SELECT r.*, p.prenom || ' ' || p.nom AS patient,
               m.prenom || ' ' || m.nom AS medecin
        FROM RENDEZ_VOUS r
        JOIN PATIENT p ON r.id_patient = p.id_patient
        JOIN MEDECIN m ON r.id_medecin = m.id_medecin
        ORDER BY r.date_heure DESC
    """).fetchall()
    conn.close()
    return render_template("rdv/liste.html", rdvs=rdvs)


@app.route("/rdv/nouveau", methods=["GET", "POST"])
@login_required
def rdv_nouveau():
    conn     = get_db()
    patients = conn.execute("SELECT * FROM PATIENT ORDER BY nom").fetchall()
    medecins = conn.execute("SELECT * FROM MEDECIN ORDER BY nom").fetchall()

    if request.method == "POST":
        id_patient = request.form["id_patient"]
        id_medecin = request.form["id_medecin"]
        date_heure = request.form["date_heure"]
        motif      = request.form.get("motif", "")
        type_rdv   = request.form.get("type", "presentiel")

        conn.execute(
            """INSERT INTO RENDEZ_VOUS (date_heure, motif, statut, type, id_patient, id_medecin)
               VALUES (?,?,'en_attente',?,?,?)""",
            (date_heure, motif, type_rdv, id_patient, id_medecin)
        )
        conn.commit()
        conn.close()
        flash("Rendez-vous créé avec succès !", "success")
        return redirect(url_for("rdv_liste"))

    conn.close()
    return render_template("rdv/nouveau.html", patients=patients, medecins=medecins)

# ============================================================
# ROUTES SUPPLEMENTAIRES RDV — à ajouter dans app.py
# Colle ce bloc juste avant : if __name__ == "__main__":
# ============================================================

@app.route("/rdv/<int:id>/confirmer")
@login_required
def rdv_confirmer(id):
    conn = get_db()
    conn.execute(
        "UPDATE RENDEZ_VOUS SET statut = 'confirme' WHERE id_rdv = ?", (id,)
    )
    conn.commit()
    conn.close()
    flash("Rendez-vous confirmé !", "success")
    return redirect(url_for("rdv_liste"))


@app.route("/rdv/<int:id>/annuler")
@login_required
def rdv_annuler(id):
    conn = get_db()
    conn.execute(
        "UPDATE RENDEZ_VOUS SET statut = 'annule' WHERE id_rdv = ?", (id,)
    )
    conn.commit()
    conn.close()
    flash("Rendez-vous annulé.", "warning")
    return redirect(url_for("rdv_liste"))


@app.route("/rdv/<int:id>/terminer")
@login_required
@role_required("admin", "medecin")
def rdv_terminer(id):
    conn = get_db()
    conn.execute(
        "UPDATE RENDEZ_VOUS SET statut = 'termine' WHERE id_rdv = ?", (id,)
    )
    conn.commit()
    conn.close()
    flash("Rendez-vous marqué comme terminé.", "info")
    return redirect(url_for("rdv_liste"))
# ============================================================
# ROUTES CONSULTATIONS + ORDONNANCES
# Colle ce bloc dans app.py juste avant : if __name__ == "__main__":
# ============================================================

@app.route("/consultations")
@login_required
def consultations_liste():
    conn = get_db()
    consultations = conn.execute("""
        SELECT c.*,
               p.prenom || ' ' || p.nom AS patient,
               m.prenom || ' ' || m.nom AS medecin
        FROM CONSULTATION c
        JOIN RENDEZ_VOUS r ON c.id_rdv = r.id_rdv
        JOIN PATIENT p     ON r.id_patient = p.id_patient
        JOIN MEDECIN m     ON r.id_medecin = m.id_medecin
        ORDER BY c.date_consultation DESC
    """).fetchall()
    conn.close()
    return render_template("consultations/liste.html", consultations=consultations)


@app.route("/consultations/nouvelle", methods=["GET", "POST"])
@login_required
@role_required("admin", "medecin")
def consultation_nouvelle():
    conn = get_db()

    # RDV terminés sans consultation existante
    rdvs = conn.execute("""
        SELECT r.id_rdv, r.date_heure,
               p.prenom || ' ' || p.nom AS patient,
               m.prenom || ' ' || m.nom AS medecin
        FROM RENDEZ_VOUS r
        JOIN PATIENT p ON r.id_patient = p.id_patient
        JOIN MEDECIN m ON r.id_medecin = m.id_medecin
        WHERE r.statut = 'termine'
          AND r.id_rdv NOT IN (SELECT id_rdv FROM CONSULTATION)
        ORDER BY r.date_heure DESC
    """).fetchall()

    if request.method == "POST":
        id_rdv      = request.form["id_rdv"]
        motif       = request.form.get("motif", "")
        diagnostic  = request.form.get("diagnostic", "")
        note        = request.form.get("note", "")
        poids       = request.form.get("poids") or None
        temperature = request.form.get("temperature") or None
        tension     = request.form.get("tension", "")

        conn.execute("""
            INSERT INTO CONSULTATION
            (motif, diagnostic, note, poids, temperature, tension, id_rdv)
            VALUES (?,?,?,?,?,?,?)
        """, (motif, diagnostic, note, poids, temperature, tension, id_rdv))
        conn.commit()
        conn.close()
        flash("Consultation enregistrée avec succès !", "success")
        return redirect(url_for("consultations_liste"))

    conn.close()
    return render_template("consultations/nouvelle.html", rdvs=rdvs)


@app.route("/consultations/<int:id>")
@login_required
def consultation_detail(id):
    conn = get_db()

    consultation = conn.execute("""
        SELECT c.*,
               p.prenom || ' ' || p.nom AS patient,
               m.prenom || ' ' || m.nom AS medecin
        FROM CONSULTATION c
        JOIN RENDEZ_VOUS r ON c.id_rdv = r.id_rdv
        JOIN PATIENT p     ON r.id_patient = p.id_patient
        JOIN MEDECIN m     ON r.id_medecin = m.id_medecin
        WHERE c.id_consultation = ?
    """, (id,)).fetchone()

    if not consultation:
        flash("Consultation introuvable.", "danger")
        return redirect(url_for("consultations_liste"))

    ordonnance = conn.execute(
        "SELECT * FROM ORDONNANCE WHERE id_consultation = ?", (id,)
    ).fetchone()

    lignes = []
    if ordonnance:
        lignes = conn.execute("""
            SELECT lo.*, med.nom, med.dosage
            FROM LIGNE_ORDONNANCE lo
            JOIN MEDICAMENT med ON lo.id_medicament = med.id_medicament
            WHERE lo.id_ordonnance = ?
        """, (ordonnance["id_ordonnance"],)).fetchall()

    conn.close()
    return render_template("consultations/detail.html",
                           consultation=consultation,
                           ordonnance=ordonnance,
                           lignes=lignes)


# ── ORDONNANCES ──────────────────────────────────────────────

@app.route("/ordonnances/nouvelle/<int:id_consultation>", methods=["GET", "POST"])
@login_required
@role_required("admin", "medecin")
def ordonnance_nouvelle(id_consultation):
    conn = get_db()

    consultation = conn.execute("""
        SELECT c.*,
               p.prenom || ' ' || p.nom AS patient
        FROM CONSULTATION c
        JOIN RENDEZ_VOUS r ON c.id_rdv = r.id_rdv
        JOIN PATIENT p     ON r.id_patient = p.id_patient
        WHERE c.id_consultation = ?
    """, (id_consultation,)).fetchone()

    medicaments = conn.execute(
        "SELECT * FROM MEDICAMENT ORDER BY nom"
    ).fetchall()

    if request.method == "POST":
        instruction = request.form.get("instruction", "")

        # Insérer l'ordonnance
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ORDONNANCE (instruction, id_consultation)
            VALUES (?, ?)
        """, (instruction, id_consultation))
        id_ordonnance = cur.lastrowid

        # Insérer les lignes
        ids_med  = request.form.getlist("id_medicament[]")
        qtes     = request.form.getlist("quantite[]")
        freqs    = request.form.getlist("frequence[]")
        durees   = request.form.getlist("duree_traitement[]")
        voies    = request.form.getlist("voie_administration[]")

        for i in range(len(ids_med)):
            if ids_med[i]:
                cur.execute("""
                    INSERT INTO LIGNE_ORDONNANCE
                    (id_ordonnance, id_medicament, quantite, frequence,
                     duree_traitement, voie_administration)
                    VALUES (?,?,?,?,?,?)
                """, (id_ordonnance, ids_med[i], qtes[i] or None,
                      freqs[i], durees[i], voies[i]))

        conn.commit()
        conn.close()
        flash("Ordonnance créée avec succès !", "success")
        return redirect(url_for("consultation_detail", id=id_consultation))

    conn.close()
    return render_template("ordonnances/nouvelle.html",
                           id_consultation=id_consultation,
                           patient=consultation["patient"],
                           medicaments=medicaments)
    # ============================================================
# ROUTES FACTURATION + LISTE D'ATTENTE
# Colle ce bloc dans app.py juste avant : if __name__ == "__main__":
# ============================================================

import datetime

# ── FACTURATION ──────────────────────────────────────────────

@app.route("/factures")
@login_required
def factures_liste():
    conn = get_db()
    factures = conn.execute("""
        SELECT f.*,
               p.prenom || ' ' || p.nom AS patient,
               pay.statut_paiement
        FROM FACTURE f
        JOIN PATIENT p ON f.id_patient = p.id_patient
        LEFT JOIN PAIEMENT pay ON f.id_facture = pay.id_facture
        ORDER BY f.date_facturation DESC
    """).fetchall()

    total_montant = conn.execute(
        "SELECT COALESCE(SUM(montant_total),0) FROM FACTURE"
    ).fetchone()[0]

    total_paye = conn.execute(
        "SELECT COALESCE(SUM(montant),0) FROM PAIEMENT WHERE statut_paiement = 'paye'"
    ).fetchone()[0]

    conn.close()
    return render_template("factures/liste.html",
                           factures=factures,
                           total_montant=total_montant,
                           total_paye=total_paye)


@app.route("/factures/nouvelle", methods=["GET", "POST"])
@login_required
@role_required("admin", "accueil")
def facture_nouvelle():
    conn     = get_db()
    patients = conn.execute("SELECT * FROM PATIENT ORDER BY nom").fetchall()

    if request.method == "POST":
        id_patient    = request.form["id_patient"]
        montant_total = request.form["montant_total"]
        mode_paiement = request.form["mode_paiement"]

        # Générer numéro de facture automatique
        today    = datetime.date.today()
        count    = conn.execute("SELECT COUNT(*) FROM FACTURE").fetchone()[0] + 1
        num_fact = f"FAC-{today.year}-{str(count).zfill(3)}"

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO FACTURE (date_facturation, montant_total, mode_paiement, num_facture, id_patient)
            VALUES (?, ?, ?, ?, ?)
        """, (today.isoformat(), montant_total, mode_paiement, num_fact, id_patient))

        id_facture = cur.lastrowid

        # Créer le paiement associé
        cur.execute("""
            INSERT INTO PAIEMENT (date_paiement, montant, mode_paiement, statut_paiement, type_paiement, id_facture)
            VALUES (?, ?, ?, 'paye', 'direct', ?)
        """, (today.isoformat(), montant_total, mode_paiement, id_facture))

        conn.commit()
        conn.close()
        flash(f"Facture {num_fact} créée avec succès !", "success")
        return redirect(url_for("factures_liste"))

    conn.close()
    return render_template("factures/nouvelle.html", patients=patients)


@app.route("/factures/<int:id>")
@login_required
def facture_detail(id):
    conn = get_db()
    facture = conn.execute("""
        SELECT f.*, p.prenom || ' ' || p.nom AS patient
        FROM FACTURE f
        JOIN PATIENT p ON f.id_patient = p.id_patient
        WHERE f.id_facture = ?
    """, (id,)).fetchone()

    paiements = conn.execute(
        "SELECT * FROM PAIEMENT WHERE id_facture = ?", (id,)
    ).fetchall()

    conn.close()
    if not facture:
        flash("Facture introuvable.", "danger")
        return redirect(url_for("factures_liste"))
    return render_template("factures/detail.html", facture=facture, paiements=paiements)


# ── LISTE D'ATTENTE ──────────────────────────────────────────

@app.route("/liste-attente")
@login_required
def liste_attente():
    conn = get_db()
    listes = conn.execute("""
        SELECT l.*, p.prenom || ' ' || p.nom AS patient
        FROM LISTE_ATTENTE l
        JOIN PATIENT p ON l.id_patient = p.id_patient
        WHERE l.statut = 'en_attente'
        ORDER BY l.niveau_priorite DESC, l.position ASC
    """).fetchall()
    conn.close()
    return render_template("liste_attente/index.html", listes=listes)


@app.route("/liste-attente/ajouter", methods=["GET", "POST"])
@login_required
@role_required("admin", "accueil")
def liste_attente_ajouter():
    conn     = get_db()
    patients = conn.execute("SELECT * FROM PATIENT ORDER BY nom").fetchall()

    if request.method == "POST":
        id_patient      = request.form["id_patient"]
        niveau_priorite = request.form.get("niveau_priorite", "normal")

        # Position suivante
        position = conn.execute(
            "SELECT COALESCE(MAX(position),0)+1 FROM LISTE_ATTENTE WHERE statut='en_attente'"
        ).fetchone()[0]

        today = datetime.date.today().isoformat()
        cur   = conn.cursor()
        cur.execute("""
            INSERT INTO LISTE_ATTENTE (date_inscription, position, statut, niveau_priorite, id_patient)
            VALUES (?, ?, 'en_attente', ?, ?)
        """, (today, position, niveau_priorite, id_patient))

        id_liste = cur.lastrowid
        cur.execute(
            "INSERT INTO LISTE_ATTENTE_PATIENT (id_patient, id_liste) VALUES (?,?)",
            (id_patient, id_liste)
        )
        conn.commit()
        conn.close()
        flash("Patient ajouté à la liste d'attente !", "success")
        return redirect(url_for("liste_attente"))

    conn.close()
    return render_template("liste_attente/ajouter.html", patients=patients)


@app.route("/liste-attente/<int:id>/appeler")
@login_required
@role_required("admin", "accueil")
def liste_attente_appeler(id):
    conn = get_db()
    conn.execute(
        "UPDATE LISTE_ATTENTE SET statut = 'appele' WHERE id_liste = ?", (id,)
    )
    conn.commit()
    conn.close()
    flash("Patient appelé !", "info")
    return redirect(url_for("liste_attente"))


@app.route("/liste-attente/<int:id>/retirer")
@login_required
@role_required("admin", "accueil")
def liste_attente_retirer(id):
    conn = get_db()
    conn.execute(
        "UPDATE LISTE_ATTENTE SET statut = 'annule' WHERE id_liste = ?", (id,)
    )
    conn.commit()
    conn.close()
    flash("Patient retiré de la liste d'attente.", "warning")
    return redirect(url_for("liste_attente"))
# ============================================================
# NOUVELLES ROUTES — Ordonnances + Notifications + Dossier
# Colle ce bloc dans app.py juste avant : if __name__ == "__main__":
# ============================================================

# ── ORDONNANCES LISTE ────────────────────────────────────────

@app.route("/ordonnances")
@login_required
def ordonnances_liste():
    conn = get_db()
    ordonnances = conn.execute("""
        SELECT o.*,
               p.prenom || ' ' || p.nom AS patient,
               m.prenom || ' ' || m.nom AS medecin,
               (SELECT COUNT(*) FROM LIGNE_ORDONNANCE lo
                WHERE lo.id_ordonnance = o.id_ordonnance) AS nb_medicaments
        FROM ORDONNANCE o
        JOIN CONSULTATION c ON o.id_consultation = c.id_consultation
        JOIN RENDEZ_VOUS r  ON c.id_rdv = r.id_rdv
        JOIN PATIENT p      ON r.id_patient = p.id_patient
        JOIN MEDECIN m      ON r.id_medecin = m.id_medecin
        ORDER BY o.date DESC
    """).fetchall()
    conn.close()
    return render_template("ordonnances/liste.html", ordonnances=ordonnances)


# ── NOTIFICATIONS ────────────────────────────────────────────

@app.route("/notifications")
@login_required
def notifications():
    conn = get_db()
    notifs = conn.execute("""
        SELECT n.*, p.prenom || ' ' || p.nom AS patient
        FROM NOTIFICATION n
        JOIN PATIENT p ON n.id_patient = p.id_patient
        ORDER BY n.lu ASC, n.id_notification DESC
    """).fetchall()
    conn.close()
    return render_template("notifications.html", notifs=notifs)


@app.route("/notifications/<int:id>/lire")
@login_required
def notification_lire(id):
    conn = get_db()
    conn.execute(
        "UPDATE NOTIFICATION SET lu = 1, statut = 'lu' WHERE id_notification = ?", (id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("notifications"))


@app.route("/notifications/lire-tout")
@login_required
def notifications_lire_tout():
    conn = get_db()
    conn.execute("UPDATE NOTIFICATION SET lu = 1, statut = 'lu'")
    conn.commit()
    conn.close()
    flash("Toutes les notifications ont été marquées comme lues.", "success")
    return redirect(url_for("notifications"))


# ── DOSSIER MÉDICAL ──────────────────────────────────────────

@app.route("/patients/<int:id>/dossier", methods=["GET", "POST"])
@login_required
def dossier_modifier(id):
    conn    = get_db()
    patient = conn.execute(
        "SELECT * FROM PATIENT WHERE id_patient = ?", (id,)
    ).fetchone()
    dossier = conn.execute(
        "SELECT * FROM DOSSIER WHERE id_patient = ?", (id,)
    ).fetchone()

    if not patient:
        flash("Patient introuvable.", "danger")
        return redirect(url_for("patients_liste"))

    if request.method == "POST":
        groupe_sanguin = request.form.get("groupe_sanguin", "")
        maladie        = request.form.get("maladie", "")
        allergies      = request.form.get("allergies", "")
        status         = request.form.get("status", "actif")

        if dossier:
            conn.execute("""
                UPDATE DOSSIER
                SET groupe_sanguin = ?, maladie = ?, allergies = ?, status = ?
                WHERE id_patient = ?
            """, (groupe_sanguin, maladie, allergies, status, id))
        else:
            conn.execute("""
                INSERT INTO DOSSIER (groupe_sanguin, maladie, allergies, status, id_patient)
                VALUES (?, ?, ?, ?, ?)
            """, (groupe_sanguin, maladie, allergies, status, id))

        conn.commit()
        conn.close()
        flash("Dossier médical mis à jour avec succès !", "success")
        return redirect(url_for("patient_detail", id=id))

    conn.close()
    return render_template("patients/dossier.html", patient=patient, dossier=dossier)
# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
