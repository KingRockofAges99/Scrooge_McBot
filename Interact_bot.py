import solana
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.keypair import Keypair
from solana.system_program import transfer, TransferParams
from solders.pubkey import Pubkey
from flask import Flask, request, jsonify
import os

# Initialize the Solana client to connect to the testnet
async def connect_to_solana():
    client = AsyncClient("https://api.testnet.solana.com")
    print("Connected to Solana Testnet")
    return client

# Function to load a keypair from Phantom Wallet (this is a placeholder)
def load_phantom_wallet():
    phantom_private_key = os.getenv("PHANTOM_PRIVATE_KEY")  # Store your private key safely
    return Keypair.from_secret_key(bytes.fromhex(phantom_private_key))

# Function to send SOL to another wallet
async def send_sol(from_keypair, to_pubkey, amount, client):
    try:
        # Create the transfer transaction
        transaction = transfer(
            TransferParams(
                from_pubkey=from_keypair.public_key,
                to_pubkey=Pubkey.from_string(to_pubkey),
                lamports=amount * 1000000000  # 1 SOL = 1 billion lamports
            )
        )
        # Send transaction
        response = await client.send_transaction(transaction, from_keypair, opts=TxOpts(skip_preflight=True))
        print("Transaction successful:", response)
        return response
    except Exception as e:
        print("Error sending SOL:", e)

# Flask API for interacting with the bot
app = Flask(__name__)

@app.route('/send', methods=['POST'])
async def send_sol_handler():
    data = request.get_json()
    from_wallet = load_phantom_wallet()
    to_address = data['to_address']
    amount = data['amount']
    client = await connect_to_solana()
    result = await send_sol(from_wallet, to_address, amount, client)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
