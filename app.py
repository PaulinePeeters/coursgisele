from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)
app.secret_key = "gisele"  # Clé secrète pour gérer la session

# Configuration de la connexion MySQL
mysql = pymysql.connect(host='ivgz2rnl5rh7sphb.chr7pe7iynqr.eu-west-1.rds.amazonaws.com',
                        user='tgbjjonzxfewfa9e',
                        password='sr3yvfd1cenotbvv',
                        database='fe9dp1x6yreethbg',
                        port=3306,
                        cursorclass=pymysql.cursors.DictCursor)


# Modèle de données de la table
class TableData:
    @staticmethod
    def fetch_all():
        with mysql.cursor() as cursor:
            cursor.execute("SELECT * FROM tabledata")
            return cursor.fetchall()

    @staticmethod
    def merge(row, col, full_name):
        with mysql.cursor() as cursor:
            cursor.execute("INSERT INTO tabledata (row, col, full_name) VALUES (%s, %s, %s) "
                           "ON DUPLICATE KEY UPDATE full_name=%s", (row, col, full_name, full_name))
            mysql.commit()

    @staticmethod
    def delete(row, col):
        with mysql.cursor() as cursor:
            cursor.execute("DELETE FROM tabledata WHERE row=%s AND col=%s", (row, col))
            mysql.commit()


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
        return redirect("/")  # Rediriger vers la page d'accueil si l'utilisateur n'est pas connecté
    full_name = session["full_name"]
    is_admin = True if full_name == "Wembalola.Eleonore" else False

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
        if is_admin:
            # L'admin peut écrire du texte dans toutes les cases
            table_data[clicked_cell] = text
            TableData.merge(row, col, text)
        else:
            # Pour les autres utilisateurs, gérer les clics sur les lignes 2 et 3
            if clicked_cell in table_data:
                if text:  # Si l'utilisateur modifie le texte, mettre à jour la ligne dans la base de données
                    table_data[clicked_cell] = text
                    TableData.merge(row, col, text)
                else:  # Sinon, supprimer la ligne de la base de données
                    del table_data[clicked_cell]
                    TableData.delete(row, col)

    return render_template("table.html", full_name=full_name, is_admin=is_admin, table_data=table_data)


if __name__ == "__main__":
    app.run(debug=True)
