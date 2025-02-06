import streamlit as st
from solana_agentkit import SolanaAgentKit
from solana_agentkit import create_solana_tools

# Initialize with private key and optional RPC URL
agent = SolanaAgentKit(
    "your-wallet-private-key-as-base58",
    "https://api.mainnet-beta.solana.com",
    "your-openai-api-key"
)

# Create LangChain tools
tools = create_solana_tools(agent)



# Constants
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
FEE_AMOUNT = 0.01
TOTAL_SUPPLY = 1000000000
POOL_LIQUIDITY_SOL = 0.1

def connect_wallet():
    wallet = WalletConnector()
    wallet_ui = wallet.connect()
    return wallet, wallet_ui

# Initialize Solana Client
solana_client = Client(SOLANA_RPC_URL)

# Initialize Agent (Assuming an AgentKit setup)
agent = Agent(solana_client)

# Streamlit UI
st.set_page_config(page_title="Solana DApp", layout="centered")
st.title("Solana Token Creator DApp")

# Wallet Connection
st.subheader("Connect your Solana Wallet")
wallet, wallet_ui = connect_wallet()
st.write(wallet_ui)

if wallet.is_connected:
    st.success(f"Connected: {wallet.public_key}")
    balance = solana_client.get_balance(wallet.public_key)['result']['value'] / 1e9
    st.write(f"SOL Balance: {balance:.4f} SOL")
else:
    st.warning("Please connect your wallet to proceed.")

# Token Creation Inputs
token_name = st.text_input("Token Name")
token_symbol = st.text_input("Token Symbol")
token_logo = st.file_uploader("Upload Token Logo", type=["png", "jpg", "jpeg"])

if st.button("Pay Fee (0.01 SOL)"):
    if wallet.is_connected and balance >= FEE_AMOUNT:
        try:
            txn = agent.transfer(wallet, agent.public_key, FEE_AMOUNT)
            st.success(f"Fee paid: {txn}")
        except Exception as e:
            st.error(f"Fee payment failed: {e}")
    else:
        st.error("Insufficient balance or wallet not connected.")

if st.button("Create Token and Pool"):
    if wallet.is_connected and token_name and token_symbol and balance >= (FEE_AMOUNT + POOL_LIQUIDITY_SOL):
        try:
            token = Token.create(agent, wallet, token_name, token_symbol, TOTAL_SUPPLY, mint_authority=None, freeze_authority=None)
            st.success(f"Token Created! Address: {token.address}")
            
            # Create Raydium Liquidity Pool
            pool = RaydiumPool.create(agent, wallet, token, POOL_LIQUIDITY_SOL, TOTAL_SUPPLY)
            st.success(f"Raydium Liquidity Pool Created! Address: {pool.address}")
            
            # Burn Liquidity Pool
            RaydiumPool.burn(agent, wallet, pool)
            st.success("Liquidity Pool Burned Successfully!")
        except Exception as e:
            st.error(f"Token or Pool creation failed: {e}")
    else:
        st.error("Ensure wallet is connected, fee is paid, and all fields are filled.")

# Footer
st.markdown("### Built with [Solana Agent Kit](https://solana.com)")
