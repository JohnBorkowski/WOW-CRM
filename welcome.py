import os, requests, json, string, datetime
from os.path import join, dirname
from random import randint
from flask import Flask, request, render_template, redirect, url_for, session
from flask.sessions import SessionInterface
from beaker.middleware import SessionMiddleware

# ------------------------------------------------
# GLOBAL VARIABLES -------------------------------
# ------------------------------------------------
#####
# CRM vars
#####
CRM_REPO = {}

#####
# Tokens
#####
CHAT_TEMPLATE = 'designer-index.html'
CUST_ID_VAR_NAME = 'cust_id'
ACCOUNT_BALANCE_VAR_NAME = 'account_balance'
HOME_ADDRESS_VAR_NAME = 'home_address'
MAILING_ADDRESS_VAR_NAME = 'mailing_address'
#####
# Session options
#####
session_opts = {
	'session.type': 'ext:memcached',
	'session.url': 'localhost:11211',
	'session.data_dir': './cache',
	'session.cookie_expires': 'true',
	'session.type': 'file',
	'session.auto': 'true'
}

# ------------------------------------------------
# CLASSES ----------------------------------------
# ------------------------------------------------
class BeakerSessionInterface(SessionInterface):
	def open_session(self, app, request):
		session = request.environ['beaker.session']
		return session

	def save_session(self, app, session, response):
		session.save()

# ------------------------------------------------
# FUNCTIONS --------------------------------------
# ------------------------------------------------
#####
# local
#####
def return_none():
	return None

# Session var set and get funcs ------------------
def s(key, value):
	session[key] = value
	return session[key]

def g(key, default_value):
	if not key in session.keys():
		session[key] = default_value
	return session[key]

def get_empty_customer_profile():
	return {"mailing_address": {"city": "", "state": "", "address_line_2": "", "zip": "", "address_line_1": ""}, "account_balance": {"current_balance": 0,"current_balance_as_of_date": ""}, "home_address": {"city": "", "state": "", "address_line_2": "", "zip": "", "address_line_1": ""}}

def get_cust_id(args):
	global CUST_ID_VAR_NAME
	cust_id = 1000000 + randint(0, 999999)
	if CUST_ID_VAR_NAME in args:
		cust_id = args[CUST_ID_VAR_NAME]
	return cust_id
	
def get_cust_profile(cust_id):
	global CUST_ID_VAR_NAME, CRM_REPO
	cust_profile = get_empty_customer_profile()
	if cust_id in CRM_REPO:
		cust_profile = CRM_REPO[cust_id]
	return cust_profile
	
def update_cust_profile(cust_id, WVA_updates):
	global CUST_ID_VAR_NAME, CRM_REPO
	customer_profile = get_cust_profile(cust_id)
	for key in WVA_updates:
		customer_profile[key] = WVA_updates[key]
	CRM_REPO[cust_id] = customer_profile
	print('--CRM_REPO[cust_id]')
	print(CRM_REPO[cust_id])
	return customer_profile
		
# ------------------------------------------------
# FLASK ------------------------------------------
app = Flask(__name__)

@app.route('/')
def Index():
	global CHAT_TEMPLATE, ACCOUNT_BALANCE_VAR_NAME, HOME_ADDRESS_VAR_NAME, MAILING_ADDRESS_VAR_NAME
	cust_id = get_cust_id(request.args)
	customer_profile = get_cust_profile(cust_id)
	return render_template(CHAT_TEMPLATE, cust_id=cust_id, profile=customer_profile)

@app.route('/', methods=['POST'])
def Index_Post():
	global CHAT_TEMPLATE
	data = json.loads(request.data)
	customer_profile = {}
	if CUST_ID_VAR_NAME in request.args:
		cust_id = request.args[CUST_ID_VAR_NAME]
		customer_profile = get_cust_profile(cust_id)
		WVA_updates = {}
		if ACCOUNT_BALANCE_VAR_NAME in data:
			WVA_updates[ACCOUNT_BALANCE_VAR_NAME] = data[ACCOUNT_BALANCE_VAR_NAME]
		if HOME_ADDRESS_VAR_NAME in data:
			WVA_updates[HOME_ADDRESS_VAR_NAME] = data[HOME_ADDRESS_VAR_NAME]
		if MAILING_ADDRESS_VAR_NAME in data:
			WVA_updates[MAILING_ADDRESS_VAR_NAME] = data[MAILING_ADDRESS_VAR_NAME]
		customer_profile = update_cust_profile(cust_id, WVA_updates)
	return render_template(CHAT_TEMPLATE, cust_id=cust_id, profile=customer_profile)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
	app.session_interface = BeakerSessionInterface()
	app.run(host='0.0.0.0', port=int(port))