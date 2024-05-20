from flask import Flask, render_template, request, redirect, session
import os
import pymysql

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gisele")  # Utilisation d'une clé secrète à partir des variables d'environnement

# Configuration de la connexion MySQL à partir des variables d'environnement
db_config = {
    'host': os.environ.get("DB_HOST", 'ivgz2rnl5rh7sphb.chr7pe7iynqr.eu-west-1.rds.amazonaws.com'),
    'user': os.environ.get("DB_USER", 'tgbjjonzxfewfa9e'),
    'password': os.environ.get("DB_PASSWORD", 'sr3yvfd1cenotbvv'),
    'database': os.environ.get("DB_DATABASE", 'fe9dp1x6yreethbg'),
    'port': int(os.environ.get("DB_PORT", 3306)),
    'cursorclass': pymysql.cursors.DictCursor
}

# Modèle de données de la table
class TableData:
    @staticmethod
    def fetch_all():
        try:
            with pymysql.connect(**db_config) as cursor:
                cursor.execute("SELECT * FROM tabledata")
                return cursor.fetchall()
        except pymysql.Error as e:
            print("Erreur lors de la récupération des données:", e)
            return []

    @staticmethod
    def merge(row, col, full_name):
        try:
            with pymysql.connect(**db_config) as cursor:
                cursor.execute("INSERT INTO tabledata (row, col, full_name) VALUES (%s, %s, %s) "
                               "ON DUPLICATE KEY UPDATE full_name=%s", (row, col, full_name, full_name))
        except pymysql.Error as e:
            print("Erreur lors de la fusion des données:", e)

    @staticmethod
    def delete(row, col):
        try:
            with pymysql.connect(**db_config) as cursor:
                cursor.execute("DELETE FROM tabledata WHERE row=%s AND col=%s", (row, col))
        except pymysql.Error as e:
            print("Erreur lors de la suppression des données:", e)


# Route de la page d'accueil
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        full_name = request.form["full_name"]
        if full_name:
            session["full_name"] = full_name
            return redirect("/table")
        else:
            return "Nom d'utilisateur incorrect. Veuillez réessayer."
    return render_template("accueil.html")


# Route de la page de la table
@app.route("/table", methods=["GET", "POST"])
def table():
    full_name = session.get("full_name")
    if not full_name:
        return redirect("/")  # Rediriger vers la page d'accueil si l'utilisateur n'est pas connecté

    is_admin = full_name == "Wembalola.Eleonore"
    
    # Récupérer les données du tableau depuis la base de données
    table_data = {}
    rows = TableData.fetch_all()
    for row in rows:
        table_data[f"cell-{row['row']}-{row['col']}"] = row['full_name']

    # Traitement des modifications dans les cellules
    if request.method == "POST":
        row = request.form["row"]
        col = request.form["col"]
        text = request.form.get("text", "")  # Récupérer le texte du formulaire

        clicked_cell = f"cell-{row}-{col}"
        if is_admin or clicked_cell in table_data:
            try:
                TableData.merge(row, col, text)
                if not text:
                    del table_data[clicked_cell]
                    TableData.delete(row, col)
                else:
                    table_data[clicked_cell] = text
            except pymysql.Error as e:
                print("Erreur lors de la mise à jour des données:", e)

    return render_template("table.html", full_name=full_name, is_admin=is_admin, table_data=table_data)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
