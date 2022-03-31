"""
File to test functionality and security of OptionDEX.sol

accounts[0]: writer A
accounts[1]: buyer A
accounts[2]: buyer B
accounts[3]: writer B
"""

import pytest
from brownie import accounts, CayugaCoin, OptionsDEX, Evil, reverts

# Fixtures
@pytest.fixture
def _CayugaCoin():
    return accounts[0].deploy(CayugaCoin, "CayugaCoin", "CC")

@pytest.fixture
def _OptionsDEX():
    return accounts[0].deploy(OptionsDEX)

# Test createOption
class Test_createOption:

    def test_one(self, _CayugaCoin, _OptionsDEX):
        """
        Testing that OptionCreated event was emitted with valid hash
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        assert str(hash) != ("0x" + "0" * 64)

    def test_two(self, _CayugaCoin, _OptionsDEX):
        """
        Testing that two options with the same initialization information do not have the same hash
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 200*(10**18))
        # Create two options
        tx_1 = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)
        tx_2 = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)
        hash_1 = tx_1.events['OptionCreated']['optionHash']
        hash_2 = tx_2.events['OptionCreated']['optionHash']
        assert str(hash_1) != str(hash_2)


# Test buyOption
# Test re-entracy attack
class Test_buyOption:

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        return hash

    def test_one(self, _CayugaCoin, _OptionsDEX, _option_hash):
        """
        Testing the successful purchase of an option
        """
        # Buy option
        _OptionsDEX.buyOption(_option_hash, {"from": accounts[1], "value" : 10**19})
        # Check holder for option
        option_data = _OptionsDEX.getOptionDetails(_option_hash)
        assert str(option_data[4]) == str(accounts[1].address)
    
    @pytest.fixture
    def evil_contract(self, _OptionsDEX, _CayugaCoin):
        """
        Creates Evil smart contract necesary for reentry attack
        """
        return accounts[0].deploy(Evil, _OptionsDEX.address, _CayugaCoin.address)


    def test_two(self, _CayugaCoin, _OptionsDEX, _option_hash, evil_contract):
        """
        Testing protection against reentry attack
        """
        # Approve for tokens to be spent by evil
        _CayugaCoin.approve(evil_contract.address, 1000 * 10**18)
        # Call setup
        tx = evil_contract.setup()
        _hash = tx.events['OptionCreated']['optionHash']
        with reverts():
            _OptionsDEX.buyOption(_hash)


# Test approveOptionTransferHolder
class Test_approveOptionTransferHolder:

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        return hash

    def test_one(self, _OptionsDEX, _CayugaCoin, _option_hash):
        """
        Tests whether approving a new holder works
        """
        # Holder A buys option
        _OptionsDEX.buyOption(_option_hash, {"from": accounts[1], "value": 10**19})
        # Holder A approves Holder B
        _OptionsDEX.approveOptionTransferHolder(_option_hash, accounts[2].address, 10**18, {"from" : accounts[1]})
        # Check that Holder B is in approvedHolderAddress mapping
        tx = _OptionsDEX.viewHolderApproval(_option_hash)
        # Assert addresses are equal
        assert tx == accounts[2].address

# Test transferOptionHolder
# Test re-entracy attack
class Test_transferOptionHolder:

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        return hash

    def test_one(self, _CayugaCoin, _OptionsDEX, _option_hash):
        """
        Tests that the transfer of an options holder (i.e. Holder A -> Holder B) is successful 
        """
        pass


# Test approveOptionTransferWriter
class Test_approveOptionTransferWriter:

    pass

# Test transferOptionWriter
# Test re-entracy attack
class Test_transferOptionWriter:

    pass

# Test exerciseOption
# Test re-entracy attack
class Test_exerciseOption:

    pass

# Test refund
class Test_refund:

    pass

# Test getOptionDetails
class Test_getOptionDetails:

    @pytest.fixture
    def _CayugaCoin(self):
        return accounts[0].deploy(CayugaCoin, "CayugaCoin", "CC")

    @pytest.fixture
    def _OptionsDEX(self):
        return accounts[0].deploy(OptionsDEX)

    def test_one(self, _CayugaCoin, _OptionsDEX):
        """
        Testing that blockExpiration is not equal to 0
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        option = _OptionsDEX.getOptionDetails(hash)
        assert int(option[5]) != 0

    def test_two(self, _CayugaCoin, _OptionsDEX):
        """
        Testing that asset address is correct
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        option = _OptionsDEX.getOptionDetails(hash)
        assert str(option[0]) == addr_coin

    def test_three(self, _CayugaCoin, _OptionsDEX):
        """
        Testing that writer address is correct
        """
        # Address of DEX contract
        addr_DEX = _OptionsDEX.address
        # Address of ERC20 token
        addr_coin = _CayugaCoin.address
        # Approve tokens to be transfered
        _CayugaCoin.approve(addr_DEX, 100*(10**18))
        # Call method createOption
        tx = _OptionsDEX.createOption(addr_coin, .1 * (10**18), 2 * 10**18, 50)

        hash = tx.events['OptionCreated']['optionHash']
        option = _OptionsDEX.getOptionDetails(hash)
        assert str(option[2]) == accounts[0].address