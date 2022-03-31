from web3 import Web3
import json
import secret

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Create smart contract
# Open contract build
f = open("./build/contracts/OptionsDEX.json")
# Format contract data
data = json.load(f)
# Close file
f.close()

# Separate Contract ABI
option_contract_abi = data["abi"]

# Create option smart contract
option_smart_contract = w3.eth.contract(address = w3.toChecksumAddress("0xc011f41d889e89F8531454B41886A65951a1c35e"), abi = option_contract_abi)

# Create ERC20 smart contract
f = open("./build/contracts/CayugaCoin.json")
data = json.load(f)
f.close()
cayugacoin_contract_abi = data["abi"]

cayugacoin_smart_contract = w3.eth.contract(address=w3.toChecksumAddress("0x26AC5B03d37448fbad9b253c16b42b0d2d34498c"), abi=cayugacoin_contract_abi)

# My address
adr = "0x4AD6402ecba289A5f3262CcD1479682D83EBD7d3"

# Approve tokens for smart contract
transaction_data = {
    'gasPrice': w3.eth.gas_price,
    'nonce' : w3.eth.get_transaction_count(adr),
    "chainId": 1337
}

# transaction = cayugacoin_smart_contract.functions.approve(w3.toChecksumAddress('0xc011f41d889e89F8531454B41886A65951a1c35e'), 10**20).buildTransaction(transaction_data)

# signed_txn = w3.eth.account.sign_transaction(transaction, secret.private_key)
# txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Create option
# transaction_2 = option_smart_contract.functions.createOption('0x26AC5B03d37448fbad9b253c16b42b0d2d34498c', 10**18, 10**18, 100).buildTransaction(transaction_data)

# signed_txn_2 = w3.eth.account.sign_transaction(transaction_2, secret.private_key)
# txn_hash_2 = w3.eth.send_raw_transaction(signed_txn_2.rawTransaction)
# print(txn_hash_2)

# Get option info

temp = option_smart_contract.functions.getOptionDetails("0xa34daccb38616f31a9a95f31b5df896510f3bc610b019987ccb65dd43122893a").call()
print(temp)