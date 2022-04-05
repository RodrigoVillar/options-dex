"""
File containing test cases for the functions of the smart contract OptionsDEX
The test cases below test the logic of OptionsDEX while also testing the security of OptionsDEX by deploying re-entrancy attacks.

The list below is a list matching holders/writers to their respective accounts:

accounts[0] = writer A
accounts[1] = holder A
accounts[2] = holder B
accounts[3] = writer B

Any test functions interacting with ERC-20 tokens utilize the CayugaCoin smart contract (writer A is given 100,000 tokens). 

Any test functions that deploy re-entrancy attacks utilize either Evil, EvilTwo, or EvilThree smart contracts 
"""

import pytest
import web3
from brownie import accounts, CayugaCoin, OptionsDEX, Evil, EvilTwo, EvilThree, reverts

# Global fixtures
@pytest.fixture
def _CayugaCoin():
    """
    Fixture that creates the CayugaCoin ERC-20 token that is utilized in test cases below. writer A deploys the smart contract. _CayugaCoin() returns the smart contract
    """
    return accounts[0].deploy(CayugaCoin, "CayugaCoin", "CC")

@pytest.fixture
def _OptionsDEX():
    """
    Fixture that creates the OptionsDEX smart contract that is utilized in test cases below. writer A deploys the smart contract. _OptionsDEX() returns the smart contract.
    """
    return accounts[0].deploy(OptionsDEX)

class Test_createOption:
    """
    Class that groups together test cases that test the function createOption()
    """

    def test_one(self, _CayugaCoin, _OptionsDEX):
        """
        Function that tests the creation of an option using the createOption.
        writer A deploys OptionsDEX, utilizing CayugaCoin the asset for the option  
        """
        # Writer A approves for 200 CayugaCoin tokens to be transferred to OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 200 * 10 ** 18, {"from": accounts[0]})
        # Create option with a premium of 0.1 eth, strikePrice of 2 eth, and a block expiration of 50
        tx = _OptionsDEX.createOption(_CayugaCoin.address, .1 * (10**18), 2 * 10**18, 50)
        # Extract option hash
        hash = tx.events['OptionCreated']['optionHash']
        # Assert that option has is not equal to the zero hash
        assert hash != ("0x" + "0" * 64), "Hash is equal to the zero hash!"

    def test_two(self, _CayugaCoin, _OptionsDEX):
        """
        Function that creates two options with the exact function arguments do not have the same hash. writer A creates option_1 (tx_1) and option_2 (tx_2) respectively. 
        """
        # Writer A approves for 200 CayugaCoin tokens to be transferred to OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 200 * 10 ** 18, {"from": accounts[0]})
        # Create "identical" options
        tx_1 = _OptionsDEX.createOption(_CayugaCoin.address, .1 * 10 ** 18, 2 * 10 ** 18, 50, {"from" : accounts[0]})
        tx_2 = _OptionsDEX.createOption(_CayugaCoin.address, .1 * 10 ** 18, 2 * 10 ** 18, 50, {"from" : accounts[0]})

        # Assert that hash from tx_1 is not equal to hash from tx_2
        assert tx_1.events["OptionCreated"]["optionHash"] != tx_2.events["OptionCreated"]["optionHash"], "Hashes are identical!"

class Test_buyOption:
    """
    Class that groups together test cases that test the function buyOption()
    """        


    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 50
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 50)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash


    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the sucessful purchase of an option. holder A is the account that will become the holder of the option defined by _option_hash.
        """
        # Holder A becomes holder of option
        _OptionsDEX.buyOption(_option_hash, {"from": accounts[1], "value" : 10 ** 19})
        # Retreive option data
        option_data = _OptionsDEX.getOptionDetails(_option_hash)
        # Assert that holder A is the holder of the option
        assert option_data[4] == accounts[1].address


    @pytest.fixture
    def evil_contract(self, _OptionsDEX, _CayugaCoin):
        """
        Fixture that deploys the Evil smart contract used in testing a re-entrancy attack against _OptionsDEX. writer A deploys the smart contract. evil_contract() returns the smart contract object.
        """
        return accounts[0].deploy(Evil, _OptionsDEX.address, _CayugaCoin.address)


    def test_two(self, _CayugaCoin, _OptionsDEX, _option_hash, evil_contract):
        """
        Function that tests the security of _OptionsDEX by initiating a re-entrancy against _OptionDEX by attempting to exploit the payable attribute of function buyOption() 
        """
        # Approve for 1000 tokens to be spent by Evil smart contract
        _CayugaCoin.approve(evil_contract.address, 1000 * 10 ** 18)
        # Call setup() in Evil
        tx = evil_contract.setup()
        # Extract created option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Test to see that re-entrancy attack is reverted by EVM
        with reverts():
            _OptionsDEX.buyOption(hash)


class Test_approveOptionTransferHolder:
    """
    Class that groups together test cases that test the function approveOptionTransferHolder()
    """

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 50
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 50)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the approval of a new option holder. _option_hash is the hash of the option that will be utilized in this test case. holder A is the account that will call _approveOptionTransferHolder() and holder B is the account that will be assigned as the approved address for the next holder.
        """
        # Holder A buys option
        _OptionsDEX.buyOption(_option_hash, {"from": accounts[1], "value": 10**19})
        # Holder A approves Holder B
        _OptionsDEX.approveOptionTransferHolder(_option_hash, accounts[2].address, 10**18, {"from" : accounts[1]})
        # Check that Holder B is in approvedHolderAddress mapping
        tx = _OptionsDEX.viewHolderApproval(_option_hash)
        # Assert addresses are equal
        assert tx == accounts[2].address, "Holder B is not the approved holder address!"


class Test_transferOptionHolder:
    """
    Class that groups together functions that test the function transferOptionHolder()
    """

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 50
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 50)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the successful transfer of the holder of an option. _option_hash is the hash of the option
        """
        # Holder A buys the option
        _OptionsDEX.buyOption(_option_hash, {"from": accounts[1], "value": 10**19})
        # Holder A calls approveOptionTransferHolder() to set Holder B as the approved holder address
        _OptionsDEX.approveOptionTransferHolder(_option_hash, accounts[2], 1, {"from": accounts[1]})
        # Holder B buys option from Holder A by calling transferOptionHolder()
        _OptionsDEX.transferOptionHolder(_option_hash, {"from": accounts[2], "value" : 1})
        # Fetch option info about option and extract option holder
        new_holder = _OptionsDEX.getOptionDetails(_option_hash)[4]
        # Assert that writer B is the holder of the option
        assert new_holder == accounts[2].address, "holder B is not the holder of this option!"

class Test_approveOptionTransferWriter:
    """
    Class that groups together test cases that test the function approveOptionTransferWriter()
    """

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 50
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 50)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the approval of writer B as the approved writer address of the option whose identifier is _option_hash. writer A is the address that is calling approveOptionTransferWriter().
        """
        # Writer A sets writer B as the approved writer address
        _OptionsDEX.approveOptionTransferWriter(_option_hash, accounts[3], 1, {"from": accounts[0]})
        # Call viewWriterApproval to get the current approved writer address
        new_writer = _OptionsDEX.viewWriterApproval(_option_hash)
        # Assert that writer B is the approved writer address
        assert new_writer == accounts[3].address, "writer B is not the approved writer address!"


class Test_transferOptionWriter:
    """
    Class that groups together test cases that test the function transferOptionWriter()
    """
    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 200
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 200)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    @pytest.fixture
    def eviltwo_contract(self, _OptionsDEX, _CayugaCoin):
        """
        Fixture that deploys the EvilTwo smart contract used in testing a re-entrancy attack against _OptionsDEX. writer A deploys the smart contract. eviltwo_contract() returns the smart contract object.
        """
        return accounts[0].deploy(EvilTwo, _OptionsDEX.address, _CayugaCoin.address)

    def test_one(self, _CayugaCoin, _OptionsDEX, _option_hash):
        """
        Function that tests the successful transfer of an option from writer A to writer B. _option_hash is the hash of the particular option being transferred. _CayugaCoin is the underlying token.
        """
        # Give Writer B tokens necessary for function to go through
        _CayugaCoin.transfer(accounts[3], 100*10**18, {"from": accounts[0]})
        # Approve Writer B as next Writer
        _OptionsDEX.approveOptionTransferWriter(_option_hash, accounts[3], 1, {"from": accounts[0]})
        # Execute transfer
        _OptionsDEX.transferOptionWriter(_option_hash, {"from": accounts[3], "value" : 1})
        # Look up option and extract address of option writer
        data = _OptionsDEX.getOptionDetails(_option_hash)
        # Assert that writer B is writer of option
        assert data[2] == accounts[3].address

    def test_two(self, _CayugaCoin, _OptionsDEX, eviltwo_contract):
        """
        Function that tests the security of _OptionsDEX by initializing a re-entrancy attack _OptionsDEX by attempting to exploit the payable attribute of transferOptionWriter()
        """
        # Give EvilTwo tokens necessary for function to go through
        _CayugaCoin.transfer(eviltwo_contract, 100 * 10**18, {"from": accounts[0]})
        # Call setup()
        tx = eviltwo_contract.setup()
        # Extract optionHash
        _hash = tx.events["OptionCreated"]["optionHash"]
        # Start reentry attack
        with reverts():
            _OptionsDEX.transferOptionWriter(_hash, {"from": accounts[0], "value": 1})


class Test_exerciseOption:
    """
    Class that groups together test cases that test the functionality of exerciseOption()
    """

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 200
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 200)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the successful exercise of an option. writer A is the writer of the option while holder A is the account that is exercising the option. _option_hash is the hash of the particular being tested. 

        test_one() also tests whether said option is deleted after it is exercised
        """
        # Holder A buys the option
        _OptionsDEX.buyOption(_option_hash, {"from": accounts[1], "value": 10**19})
        # Holder A exercises the option
        tx = _OptionsDEX.exerciseOption(_option_hash, {"from": accounts[1], "value": 200 * 10**18})
        # Check that ERC20 tokens were transferred by extracting event
        # Extract "to" address
        to_address = tx.events["Transfer"]["to"]
        # Extract "from" address
        from_address = tx.events["Transfer"]["from"]
        # Assert that "from" address is _OptionsDEX and that "to" address is holder A
        assert to_address == accounts[1].address and from_address == _OptionsDEX.address, "'to' address or 'from' address of ERC20 transfer is incorrect"    

        # Look up option using hash
        tx = _OptionsDEX.getOptionDetails(_option_hash)
        # Assert that option does not exist
        assert tx[5] == 0, "This option was not deleted!"

    @pytest.fixture
    def evilthree_contract(self, _OptionsDEX, _CayugaCoin):
        """
        Fixture that deploys the EvilThree smart contract used in the re-entrancy attack of function exercise(). writer A is the account that deploys the smart contract. evilthree_contract() returns the smart contract object
        """
        return accounts[0].deploy(EvilThree, _OptionsDEX.address, _CayugaCoin.address)

    def test_two(self, evilthree_contract, _OptionsDEX, _CayugaCoin):
        """
        Function that tests the security of exercise() by deploying a re-entrancy attack against OptionsDEX utilizing said function as a gateway. 
        """
        # Give EvilThree tokens necessary for function to go through
        _CayugaCoin.transfer(evilthree_contract, 100 * 10**18, {"from": accounts[0]})
        # Call setup
        tx = evilthree_contract.setup()
        # Extract optionHash
        _hash = tx.events['OptionCreated']['optionHash']
        # Holder A buys option
        _OptionsDEX.buyOption(_hash, {"from": accounts[1], "value": 10 ** 19})
        # Start reentry attack
        with reverts():
            _OptionsDEX.exerciseOption(_hash, {"from": accounts[1], "value": 2 * 10 ** 18})

class Test_refund:
    """
    Class that groups together test cases that tests the functionality of refund()
    """

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 200
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 200)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the correct refund of funds to the writer of an option. writer A is the account being refunded and _option_hash is the hash of the option being refunded
        """
        # Call refund function
        _OptionsDEX.refund(_option_hash)
        # Get (deleted) option details
        tx = _OptionsDEX.getOptionDetails(_option_hash)
        # Extract block number
        num = tx[5]
        # Assert that option was deleted
        assert num == 0, "The option was not deleted!"


class Test_getOptionDetails:
    """
    Class that groups together test cases that test the functionality of getOptionDetails()
    """

    @pytest.fixture
    def _option_hash(self, _CayugaCoin, _OptionsDEX):
        """
        Fixture that returns the hash of a created option.

        _option_hash() calls createOption() from writer A and extracts the hash of the created option by accessing the event OptionCreated from the transaction data.

        Data of created option:
        - Asset: CayugaCoin
        - Premium: 0.1 eth
        - Strike Price: 2 eth
        - Block Expiration: 200
        """
        # Approve for 100 CayugaCoin tokens to be transferred to _OptionsDEX
        _CayugaCoin.approve(_OptionsDEX.address, 100 * 10 ** 18)
        # Create option
        tx = _OptionsDEX.createOption(_CayugaCoin.address, 0.1 * 10 ** 18, 2 * 10 ** 18, 200)
        # Extract option hash from transaction
        hash = tx.events["OptionCreated"]["optionHash"]
        # Return option hash
        return hash

    def test_one(self, _OptionsDEX, _option_hash):
        """
        Function that tests the functionality of getOptionDetails() by testing whether if the function returns the correct block expiration of the option. _option_hash is the hash of the option used in testing.
        """
        # Call getOptionDetails()
        tx = _OptionsDEX.getOptionDetails(_option_hash)
        # Extract block number from transaction
        block_num = tx[5]
        # Assert that block_num is 200
        assert block_num == 200, "getOptionDetails() returned the wrong block number!"

    def test_two(self, _CayugaCoin, _OptionsDEX, _option_hash):
        """
        Function that tests the functionality of getOptionDetails() by testing whether if the function returns the correct address of the option asset. _option_hash is the hash of the option used in testing.
        """
        # Call getOptionDetails()
        tx = _OptionsDEX.getOptionDetails(_option_hash)
        # Extract option asset from transaction
        asset_address = tx[0]
        # Assert that asset_address is the address of the option asset
        assert asset_address == _CayugaCoin.address, "getOptionDetails() returned the wrong asset address!"

    def test_three(self, _OptionsDEX, _option_hash):
        """
        Function that tests the functionality of getOptionDetails() by testing whether if the function returns the correct address of the option writer. _option_hash is the hash of the option used in testing.
        """
        # Call getOptionDetails()
        tx = _OptionsDEX.getOptionDetails(_option_hash)
        # Extract option writer from transaction
        writer_address = tx[2]
        # Assert that writer_address is the address of the option writer
        assert writer_address == accounts[0].address, "getOptionDetails() returned the wrong writer address!"

    def test_four(self, _OptionsDEX, _option_hash):
        """
        Function that tests the functionality of getOptionDetails() by testing whether if the function returns the correct address of the option holder. _option_hash is the hash of the option used in testing.
        """
        # Call getOptionDetails()
        tx = _OptionsDEX.getOptionDetails(_option_hash)
        # Extract option holder from transaction
        holder_address = tx[4]
        # Assert that holder_address is the address of the option holder
        assert holder_address == '0x0000000000000000000000000000000000000000', "getOptionDetails() returned the wrong holder address!" 
