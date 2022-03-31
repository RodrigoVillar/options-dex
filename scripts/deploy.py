from brownie import HelloWorld, accounts

def main():
    acct = accounts.load('main')
    return HelloWorld.deploy({'from': acct})