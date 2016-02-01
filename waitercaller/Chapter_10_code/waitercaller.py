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
#from mockdbhelper import MockDBHelper as DBHelper
if config.test:
	from mockdbhelper import MockDBHelper as DBHelper
else:
	from dbhelper import DBHelper
from user import User
from bitlyhelper import BitlyHelper
from forms import RegistrationForm
from forms import LoginForm
from forms import CreateTableForm

ROOT_URL = "http://127.0.0.1:5000/"

DB = DBHelper("waitercaller")
PH = PasswordHelper()
BH = BitlyHelper()

app = Flask(__name__)
app.secret_key = config.secret_key
login_manager = LoginManager(app)


@app.route("/")
def home():
	return render_template("home.html", loginform=LoginForm(), registrationform=RegistrationForm())


@app.route("/login", methods=["POST"])
def login():
	form = LoginForm(request.form)
	if form.validate():
		stored_user = DB.get_user(form.email.data)
		if stored_user and PH.validate_password(form.password.data, stored_user['salt'], stored_user['hashed']):
			user = User(form.email.data)
			login_user(user, remember=True)
			return redirect(url_for('account'))
		form.email.errors.append("Email or password invalid")
	return render_template("home.html", loginform=form, registrationform=RegistrationForm())


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
			return render_template("home.html", loginform=LoginForm(), 	registrationform=form)
		salt = PH.get_salt()
		hashed = PH.get_hash(form.password2.data + salt)
		DB.add_user(form.email.data, salt, hashed)
		return render_template("home.html", loginform=LoginForm(), registrationform=form, onloadmessage="Registration successful. Please log in.")
	return render_template("home.html", loginform=LoginForm(), registrationform=form)


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
		deltaseconds = (now - x['time']).seconds
		x['wait_minutes'] = "{}.{}".format((deltaseconds/60), str(deltaseconds % 60).zfill(2))
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
	return render_template("account.html", createtableform=CreateTableForm(request.form), tables=tables)


@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        new_url = BH.shorten_url(ROOT_URL + "newrequest/" + str(tableid))
        DB.update_table(tableid, new_url)
        return redirect(url_for('account'))
    return render_template("account.html", createtableform=form, tables=DB.get_tables(current_user.get_id()))


@app.route("/account/deletetable")
@login_required
def account_deletetable():
	tableid = request.args.get("tableid")
	DB.delete_table(tableid)
	return redirect(url_for('account'))


@app.route("/newrequest/<tid>")
def new_request(tid):
        if DB.add_request(tid, datetime.datetime.now()):
            return "Your request has been logged and a waiter will be with you shortly"
        return "There is already a request pending for this table. Please be patient, a waiter will be there ASAP"



if __name__ == '__main__':
	app.run(debug=True)