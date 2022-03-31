"""
File to test functionality and security of OptionDEX.sol
"""

import pytest
from brownie import accounts, CayugaCoin, OptionsDEX, convert

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


# Test buyOption
# Test re-entracy attack
class Test_buyOption:

    pass

# Test approveOptionTransferHolder
class Test_approveOptionTransferHolder:

    pass

# Test transferOptionHolder
# Test re-entracy attack
class Test_transferOptionHolder:

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