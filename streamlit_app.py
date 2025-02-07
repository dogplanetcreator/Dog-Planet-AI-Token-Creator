from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import transfer, TransferParams
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import mint_to, create_mint
from solders.pubkey import Pubkey
import base58
from flask import Flask, request, jsonify

app = Flask(__name__)

# Connect to Solana Devnet or Mainnet
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"  # Change to devnet if needed
client = Client(SOLANA_RPC_URL)

# Public key for fee receiver
FEE_RECEIVER_PUBKEY = Pubkey("YOUR_FEE_RECEIVER_PUBLIC_KEY")

# Charge 0.01 SOL fee
def charge_fee(signed_tx):
    response = client.send_raw_transaction(signed_tx)
    return response

# Create Token Mint
def create_token_mint(authority_pubkey):
    token = Token.create_mint(
        client,
        authority_pubkey,
        authority_pubkey,
        9,  # Decimals
        TOKEN_PROGRAM_ID
    )
    return token.pubkey

# Mint tokens to an account
def mint_tokens(token_mint, recipient_pubkey, amount, authority_pubkey):
    tx = Transaction()
    tx.add(
        mint_to(
            mint=token_mint,
            dest=recipient_pubkey,
            authority=authority_pubkey,
            amount=amount
        )
    )
    response = client.send_transaction(tx, authority_pubkey)
    return response

# Create Raydium Pool (Placeholder, requires interaction with Raydium SDK)
def create_raydium_pool(token_mint, fee_payer_pubkey):
    print(f"Creating Raydium Pool for Token: {token_mint}")
    return "Raydium Pool Created"

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    data = request.json
    fee_payer_pubkey = data.get("fee_payer_pubkey")
    if not fee_payer_pubkey:
        return jsonify({"error": "Fee payer public key is required"}), 400
    return jsonify({"message": "Wallet connected", "fee_payer_pubkey": fee_payer_pubkey})

@app.route('/phantom_connect', methods=['GET'])
def phantom_connect():
    return jsonify({"message": "Open Phantom Wallet and approve the connection."})

@app.route('/charge_fee', methods=['POST'])
def charge_fee_endpoint():
    data = request.json
    signed_tx = data.get("signed_tx")
    if not signed_tx:
        return jsonify({"error": "Signed transaction is required"}), 400
    fee_response = charge_fee(base58.b58decode(signed_tx))
    return jsonify({"message": "Fee transaction sent", "response": fee_response})

@app.route('/create_pool', methods=['POST'])
def create_pool_endpoint():
    data = request.json
    fee_payer_pubkey = data.get("fee_payer_pubkey")
    authority_pubkey = data.get("authority_pubkey")
    if not fee_payer_pubkey or not authority_pubkey:
        return jsonify({"error": "Fee payer and authority public key are required"}), 400
    
    token_mint = create_token_mint(Pubkey(authority_pubkey))
    mint_tokens(token_mint, Pubkey("Raydium_LP_Wallet"), 900000000 * (10**9), Pubkey(authority_pubkey))
    mint_tokens(token_mint, Pubkey(fee_payer_pubkey), 100000000 * (10**9), Pubkey(authority_pubkey))
    response = create_raydium_pool(token_mint, Pubkey(fee_payer_pubkey))
    return jsonify({"message": "Pool created", "response": response})

@app.route('/burn_raydium_pool', methods=['POST'])
def burn_raydium_pool_endpoint():
    data = request.json
    pool_pubkey = data.get("pool_pubkey")
    if not pool_pubkey:
        return jsonify({"error": "Pool public key is required"}), 400
    response = burn_raydium_pool(Pubkey(pool_pubkey))
    return jsonify({"message": response})

if __name__ == "__main__":
    app.run(debug=True)
