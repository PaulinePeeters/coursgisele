from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "gisele"  # Clé secrète pour gérer la session

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tgbjjonzxfewfa9e:sr3yvfd1cenotbvv@ivgz2rnl5rh7sphb.chr7pe7iynqr.eu-west-1.rds.amazonaws.com:3306/fe9dp1x6yreethbg'
db = SQLAlchemy(app)

# Modèle de données de la table
class TableData(db.Model):
    row = db.Column(db.String(50), primary_key=True)
    col = db.Column(db.String(50), primary_key=True)
    full_name = db.Column(db.String(255))
    
    def __repr__(self):
        return f"TableData(row={self.row}, col={self.col}, full_name={self.full_name})"

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
    rows = TableData.query.all()
    for row in rows:
        table_data[f"cell-{row.row}-{row.col}"] = row.full_name

    # Traitement des modifications dans les cellules
    if request.method == "POST":
        row = request.form["row"]
        col = request.form["col"]
        text = request.form.get("text", "")  # Récupérer le texte du formulaire

        clicked_cell = f"cell-{row}-{col}"
        if is_admin:
            # L'admin peut écrire du texte dans toutes les cases
            table_data[clicked_cell] = text
            new_data = TableData(row=row, col=col, full_name=text)
            db.session.merge(new_data)
        else:
            # Pour les autres utilisateurs, gérer les clics sur les lignes 2 et 3
            current_data = TableData.query.filter_by(row=row, col=col).first()
            if current_data and current_data.full_name == full_name:
                if text:  # Si l'utilisateur modifie le texte, mettre à jour la ligne dans la base de données
                    current_data.full_name = text
                    db.session.commit()
                else:  # Sinon, supprimer la ligne de la base de données
                    db.session.delete(current_data)
                    table_data.pop(clicked_cell)
        db.session.commit()

    return render_template("table.html", full_name=full_name, is_admin=is_admin, table_data=table_data)


if __name__ == "__main__":
    app.run(debug=True)
