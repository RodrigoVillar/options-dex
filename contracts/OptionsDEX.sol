// SPDX-License-Identifier: MIT

pragma solidity 0.8.0;

import "../interfaces/IERC20.sol";
import "../interfaces/IOptionsDEX.sol";

/*
Options DEX smart contract
*/
contract OptionsDEX is IOptionsDEX {

    struct Option {
        // Address of ERC20 asset
        address asset;
        // Right to buy token at strikePrice (in Wei)
        uint96 strikePrice;
        // Address of option writer
        address writer;
        // Premium per token (in Wei)
        uint96 premium;
        // Address of option holder
        address holder;
        // Expiration block #
        uint96 blockExpiration;
        // Holder's sell price (if existent) (in Wei)
        uint128 holderSellPrice;
        // Writer's sell price (if existent) (in Wei)
        uint128 writerSellPrice;
    }

    // Hash of option to option
    mapping(bytes32 => Option) private openOptions;
    // Address to nonce
    mapping(address => uint32) private addressNonce;
    // Hash of option to approved new holder
    mapping(bytes32 => address) private approvedHolderAddress;
    // Hash of option to approved new writer
    mapping(bytes32 => address) private approvedWriterAddress;

    // Event detailing creation of new option
    event OptionCreated(address indexed seller, bytes32 indexed optionHash);

    // Event detailing purchase of an option either by a holder or writer
    event OptionExchanged(bytes32 indexed optionHash);

    function createOption(address _asset, uint96 _premium, uint96 _strikePrice, uint96 _blockExpiration) public override {
        // Enforce preconditions
        // Check that _blockExpiration is for future block
        require(_blockExpiration > block.number, "Invalid block expiration!");
        // Check that _premium is a valid number
        require(_premium > 0, "Invalid premium!");
        // Check that _strikePrice is a valid number
        require(_strikePrice > 0, "Invalid strike price!");

        // Create option
        Option memory _option = Option(_asset, _strikePrice, msg.sender, _premium, address(0), _blockExpiration, 0, 0);
        // Create hash for option
        bytes32 _optionHash = keccak256(abi.encode(_option, addressNonce[msg.sender]));
        // Add option to mapping
        openOptions[_optionHash] = _option;
        // Increment account nonce
        addressNonce[msg.sender] += 1;

        // Create interface
        IERC20 _token = IERC20(_asset);
        // Check that user has enough tokens to cover option
        require(_token.balanceOf(msg.sender) >= 100, "Not enough tokens to cover option!");
        // Transfer 100 tokens to smart contract
        _token.transferFrom(msg.sender, address(this), 100);

        // Emit new option
        emit OptionCreated(msg.sender, _optionHash);
    }

    function buyOption(bytes32 _optionHash) payable public override {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check premium * 100 is equal to eth sent
        require(msg.value == _option.premium * 100, "Incorrect amount sent!");
        // Check option does not already have holder
        require(_option.holder == address(0), "This option has already been bought!");

        // Set holder directly in storage
        openOptions[_optionHash].holder = msg.sender;
        // Send eth to writer
        payable(_option.holder).call{value : msg.value};
        // Emit option buy
        emit OptionExchanged(_optionHash);
    }

    function approveOptionTransferHolder(bytes32 _optionHash, address _newBuyer, uint128 _price) public override {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check that current holder is calling this option
        require(msg.sender == _option.holder, "You are not the current holder!");

        // Set holderSellPrice for option
        openOptions[_optionHash].holderSellPrice = _price;
        // Add _newBuyer to approved addresses
        approvedHolderAddress[_optionHash] = _newBuyer;
    }

    function transferOptionHolder(bytes32 _optionHash) public payable override {
        // Check that msg.sender has permission
        require(approvedHolderAddress[_optionHash] == msg.sender, "You are not authorized!");
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check that msg.value is equal to holder's sell price
        require(_option.holderSellPrice == msg.value, "Incorrect amount sent!");

        // Change option holder
        openOptions[_optionHash].holder = msg.sender;
        // Delete approved address
        delete approvedHolderAddress[_optionHash];

        // Send ETH to past holder
        payable(_option.holder).call{value : msg.value};

    }

    function approveOptionTransferWriter(bytes32 _optionHash, address _newWriter, uint128 _price) public override {
         // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check that current holder is calling this option
        require(msg.sender == _option.holder, "You are not the current holder!");

        // Set holderSellPrice for option
        openOptions[_optionHash].writerSellPrice = _price;
        // Add _newBuyer to approved addresses
        approvedWriterAddress[_optionHash] = _newWriter;
    }

    function transferOptionWriter(bytes32 _optionHash) public payable override {
        // Check that msg.sender has permission
        require(approvedWriterAddress[_optionHash] == msg.sender, "You are not authorized!");
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check that msg.value is equal to holder's sell price
        require(_option.holderSellPrice == msg.value, "Incorrect amount sent!");
        // Check that msg.sender has enough assets to cover option
        IERC20 _token = IERC20(_option.asset);
        require(_token.balanceOf(msg.sender) >= 100, "You do not have the assets necessary to cover this call");

        // Change option writer
        openOptions[_optionHash].writer = msg.sender;
        // Delete approved address
        delete approvedWriterAddress[_optionHash];

        // Send ETH to past holder
        payable(_option.writer).call{value : msg.value};

    }

    function exerciseOption(bytes32 _optionHash) public payable override {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check that msg.sender is current holder
        require(_option.holder == msg.sender, "You are not the holder!");
        // Check that eth sent = strikePrice * 100
        require(msg.value == _option.strikePrice * 100, "Incorrect amount sent!");

        // Send tokens to msg.sender
        IERC20 _token = IERC20(_option.asset);
        _token.transfer(msg.sender, 100);

        // Delete option
        delete openOptions[_optionHash];
        // Send ETH to writer
        payable(_option.writer).call{value : msg.value};
    }

    function refund(bytes32 _optionHash) public override {
        // Fetch option from storage and check if it is valid
        Option memory _option = openOptions[_optionHash]; 
        // Check that option is past block expiration or that no buyer has been assigned
        require(block.number > _option.blockExpiration || _option.holder == address(0), "You are not able to be refunded!");
        // Check that msg.sender is the option writer
        require(msg.sender == _option.writer, "You are not the option writer!");

        // Send 100 tokens back to seller
        IERC20 _token = IERC20(_option.asset);
        _token.transfer(msg.sender, 100);

        // Delete option from storage
        delete openOptions[_optionHash];
        delete approvedHolderAddress[_optionHash];
        delete approvedHolderAddress[_optionHash];
    }

    function getOptionDetails(bytes32 _optionHash) public view override returns(address, uint96, address, uint96, address, uint96, uint128, uint128) {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Return option as tuple
        return (_option.asset, _option.strikePrice, _option.writer, _option.premium, _option.holder, _option.blockExpiration, _option.holderSellPrice, _option.writerSellPrice);
    }

    function viewHolderApproval(bytes32 _optionHash) external view override returns (address) {
        return approvedHolderAddress[_optionHash];
    }

    function viewWriterApproval(bytes32 _optionHash) external view override returns (address) {
        return approvedWriterAddress[_optionHash];
    }

    receive() external payable override {}
}