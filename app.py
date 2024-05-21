from flask import Flask, render_template, request, redirect, session
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
    def fetch_all():
        try:
            with pymysql.connect(**db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM tabledata")
                    return cursor.fetchall()
        except pymysql.Error as e:
            print("Erreur lors de la récupération des données:", e)
            return []

    @staticmethod
    def merge(row, col, full_name):
        try:
            with pymysql.connect(**db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO tabledata (row, col, full_name) VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE full_name=%s",
                        (row, col, full_name, full_name)
                    )
                conn.commit()  # Ensure changes are committed
        except pymysql.Error as e:
            print("Erreur lors de la fusion des données:", e)

    @staticmethod
    def delete(row, col):
        try:
            with pymysql.connect(**db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM tabledata WHERE row=%s AND col=%s", (row, col))
                conn.commit()  # Ensure changes are committed
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
    cursor = get_cursor()

    cursor.execute("SELECT row_num, col_num, full_name FROM tabledata")
    rows = cursor.fetchall()
    table_data = {}
    if rows:
        table_data = {f"cell-{row['row_num']}-{row['col_num']}": row['full_name'] for row in rows}

    if request.method == "POST":
        row = request.form["row"]
        col = request.form["col"]
        new_value = request.form["value"]
        clicked_cell = f"cell-{row}-{col}"
        table_data[clicked_cell] = new_value

        cursor.execute("DELETE FROM tabledata WHERE row_num = %s AND col_num = %s", (row, col))
        if new_value:
            cursor.execute("INSERT INTO tabledata (row_num, col_num, full_name) VALUES (%s, %s, %s)",
                           (row, col, new_value))
        db.commit()

    return render_template("table.html", full_name=full_name, is_admin=is_admin, table_data=table_data)
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
