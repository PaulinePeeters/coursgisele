from flask import Flask, render_template, request, redirect, session, g
import os
import pymysql

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gisele")

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
    def merge(row, col, full_name):
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tabledata (row_num, col_num, full_name) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE full_name=%s",
                    (row, col, full_name, full_name)
                )
            # Appeler commit sur la connexion (g.db) après l'exécution de la requête
            g.db.commit()  # Ensure changes are committed
        except pymysql.Error as e:
            print("Erreur lors de la fusion des données:", e)

    @staticmethod
    def delete(row, col):
        try:
            with get_cursor() as cursor:
                cursor.execute("DELETE FROM tabledata WHERE row_num=%s AND col_num=%s", (row, col))
            # Appeler commit sur la connexion (g.db) après l'exécution de la requête
            g.db.commit()  # Ensure changes are committed
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
    if "full_name" not in session:
        return redirect("/")
    full_name = session["full_name"]
    is_admin = full_name == "Wembalola.Eleonore"

    # Récupérer les données du tableau depuis la base de données
    table_data = {}
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT row_num, col_num, full_name FROM tabledata")
            rows = cursor.fetchall()
            for row in rows:
                table_data[f"cell-{row['row_num']}-{row['col_num']}"] = row['full_name']
    except pymysql.Error as e:
        print("Erreur lors de la récupération des données:", e)

    # Traitement des modifications dans les cellules
    if request.method == "POST":
        row = request.form["row"]
        col = request.form["col"]
        text = request.form.get("text", "")

        clicked_cell = f"cell-{row}-{col}"
        if is_admin or clicked_cell in table_data or (not is_admin and int(row) <= 2):
            try:
                if text:
                    TableData.merge(row, col, text)
                    table_data[clicked_cell] = text
                else:
                    TableData.delete(row, col)
                    table_data.pop(clicked_cell, None)
            except pymysql.Error as e:
                print("Erreur lors de la mise à jour des données:", e)

    return render_template("table.html", full_name=full_name, is_admin=is_admin, table_data=table_data)

def get_cursor():
    if 'db' not in g:
        g.db = pymysql.connect(**db_config)
    return g.db.cursor()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
