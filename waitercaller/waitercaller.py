from flask import Flask, render_template, request
from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user, logout_user
from flask import redirect
from flask import url_for
from passwordhelper import PasswordHelper
from flask.ext.login import current_user
import datetime

import dbconfig as config
from mockdbhelper import MockDBHelper as DBHelper
from user import User
from bitlyhelper import BitlyHelper

from forms import RegistrationForm

ROOT_URL = "http://127.0.0.1:5000/"

DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()

app = Flask(__name__)
app.secret_key = config.secret_key
login_manager = LoginManager(app)


@app.route("/")
def home():
	registrationform = RegistrationForm()
	return render_template("home.html", registrationform=registrationform)


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    stored_user = DB.get_user(email)
    if stored_user and PH.validate_password(password, stored_user['salt'], stored_user['hashed']):
        user = User(email)
        login_user(user, remember=True)
        return redirect(url_for('account'))
    return home()


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))


@app.route("/register", methods=["POST"])
def register():
	form = RegistrationForm(request.form)
	if form.validate():
		if DB.get_user(form.email.data):
			form.email.errors.append("Email address already registered")
			return render_template('home.html', registrationform=form)
		salt = PH.get_salt()
		hashed = PH.get_hash(form.password2.data + salt)
		DB.add_user(form.email.data, salt, hashed)
		return redirect(url_for('home'))
	return render_template('home.html', registrationform=form)
'''
    email = request.form.get("email")
    pw1 = request.form.get("password")
    pw2 = request.form.get("password2")
    if not pw1 == pw2:
        return  redirect(url_for('home'))
    if DB.get_user(email):
        return redirect(url_for('home'))
    salt = PH.get_salt()
    hashed = PH.get_hash(pw1)
    hashed = PH.get_hash(pw1 + salt)
    DB.add_user(email, salt, hashed)
    return redirect(url_for('home'))
'''

@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
    	return User(user_id)


@app.route("/dashboard")
@login_required
def dashboard():
	now = datetime.datetime.now()
	requests = DB.get_requests(current_user.get_id())
	for x in requests:
		deltaseconds = (now - requests[x]['time']).seconds
		requests[x]['wait_minutes'] = "{}.{}".format((deltaseconds/60), str(deltaseconds % 60).zfill(2))
	return render_template("dashboard.html", requests=requests)


@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
	request_id = request.args.get("request_id")
	DB.delete_request(request_id)
	return redirect(url_for('dashboard'))


@app.route("/account")
@login_required
def account():
	tables = DB.get_tables(current_user.get_id())
	return render_template("account.html", tables=tables)


@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
	tablename = request.form.get("tablenumber")
	tableid = DB.add_table(tablename, current_user.get_id())
	new_url = BH.shorten_url(ROOT_URL + "newrequest/" + tableid)
	DB.update_table(tableid, new_url)
	return redirect(url_for('account'))


@app.route("/account/deletetable")
@login_required
def account_deletetable():
	tableid = request.args.get("tableid")
	DB.delete_table(tableid)
	return redirect(url_for('account'))


@app.route("/newrequest/<tid>")
def new_request(tid):
	DB.add_request(tid, datetime.datetime.now())
	return "Your request has been logged and a waiter will be with you shortly"



if __name__ == '__main__':
	app.run(debug=True)