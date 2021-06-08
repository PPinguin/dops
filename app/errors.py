from flask import render_template
from app import app, db

@app.errorhandler(400)
def error400(error):
    return render_template("400.html"), 400

@app.errorhandler(500)
def error500(error):
    db.session.rollback()
    return render_template("500.html"), 500