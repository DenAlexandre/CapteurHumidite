from flask import Flask, render_template, redirect, url_for, request, session, abort, flash

from app import app

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/courbe')
def contact():
    return render_template("courbe.html")

@app.route('/gestion')
def gestion():
    return render_template("gestion.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' and request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('Successful login.')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))
