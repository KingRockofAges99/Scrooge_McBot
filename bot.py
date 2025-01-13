import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import numpy as np
import pandas as pd
import json

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Route for the homepage/dashboard
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html')

# Route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Route for registering a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Function to fetch historical data
def fetch_historical_data(pair_address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['pair']['volumeChart']
        df = pd.DataFrame(data, columns=['timestamp', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except requests.RequestException as e:
        print(f"Error fetching historical data: {e}")
        return None

# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)

# --- Solana Integration ---
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
import json

# Connect to Solana Testnet
solana_client = Client("https://api.testnet.solana.com")

# Check the connection status
def check_connection():
    status = solana_client.get_health()
    print(f"Solana Testnet status: {status['result']}")

# Function to check wallet balance
def get_balance(public_key_str):
    public_key = PublicKey(public_key_str)
    balance = solana_client.get_balance(public_key)
    sol_balance = balance['result']['value'] / 1_000_000_000  # Convert lamports to SOL
    print(f"Wallet balance: {sol_balance} SOL")

# Load your Phantom wallet
def load_wallet():
    with open("phantom_wallet.json", "r") as f:
        secret_key = json.load(f)
    return Keypair.from_secret_key(bytes(secret_key))

# Function to send SOL
def send_sol(sender_keypair, recipient_pubkey_str, amount):
    recipient_pubkey = PublicKey(recipient_pubkey_str)
    txn = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=sender_keypair.public_key,
                to_pubkey=recipient_pubkey,
                lamports=int(amount * 1_000_000_000),  # Convert SOL to lamports
            )
        )
    )
    response = solana_client.send_transaction(txn, sender_keypair)
    print(f"Transaction signature: {response['result']}")

# Test the Solana connection
check_connection()

# Replace with your Phantom wallet public key
get_balance("2JsqQjx6fyRt4ihB1iammjPxFbBSYBXs87xru8KFKPnp")

import json
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

# ✅ Connect to Solana Testnet
solana_client = Client("https://api.testnet.solana.com")

# ✅ Load your wallet from a JSON file
def load_wallet(filename="phantom_wallet.json"):
    with open(filename, "r") as f:
        secret_key = json.load(f)
    return Keypair.from_secret_key(bytes(secret_key))

# ✅ Check wallet balance
def get_balance(public_key_str):
    public_key = PublicKey(public_key_str)
    balance = solana_client.get_balance(public_key)
    sol_balance = balance['result']['value'] / 1_000_000_000  # Convert lamports to SOL
    print(f"💰 Wallet balance: {sol_balance} SOL
