pragma solidity 0.8.0;

/*
Interface for ERC20 token
*/
interface IERC20 {

    function totalSupply() external view returns (uint);

    function balanceOf(address account) external view returns (uint);

    function transfer(address recipient, uint amount) external returns (bool);

    function allowance(address owner, address spender) external view returns (uint);

    function approve(address spender, uint amount) external returns (bool);

    function transferFrom(
        address sender,
        address recipient,
        uint amount
    ) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint value);
    event Approval(address indexed owner, address indexed spender, uint value);

}


/*
Interface for OptionsDex
*/
interface IOptionsDex {

    function createOption(address _asset, uint256 _premium, uint256 _strikePrice, uint64 _blockExpiration) external;

    function buyOption(bytes32 _optionHash) payable external;

    function approveOptionTransfer(bytes32 _optionHash, address _newBuyer, uint256 _price) external;

    function transferOption(bytes32 _optionHash) payable external;

    function exerciseOption(bytes32 _optionHash) payable external;

    function refund(bytes32 _optionHash) external;

    function getOptionDetails(bytes32) external view returns (address, address, address, uint64, uint32, uint256, uint256, uint256);

}

/*
Options DEX smart contract
*/
contract OptionsDEX is IOptionsDex {

    struct Option {
        // Address of ERC-20 asset
        address asset;
        // Address of writer
        address writer;
        // Address of holder
        address holder;
        // Expiration block #
        uint64 blockexpiration;
        // Nonce to prevent identical transactions
        uint32 sellerNonce;
        // Premium per token (in Wei)
        uint256 premium;
        // Right to buy token at strikePrice (in Wei)
        uint256 strikePrice;
        // Holder's sell price (if existent)
        uint256 holderSellPrice;
    }

    // Hash of option to option
    mapping(bytes32 => Option) private openOptions;
    // Address to nonce
    mapping(address => uint32) private addressNonce;
    // Hash of option to approved address
    mapping(bytes32 => address) private approvedAddress;

    // Event detailing creation of new option
    event OptionCreated(address indexed seller, bytes32 indexed optionHash);
    // Event detailing purchase of an option
    event OptionBought(bytes32 optionHash);

    function createOption(address _asset, uint256 _premium, uint256 _strikePrice, uint64 _blockExpiration) public override {
        // Enforce preconditions
        // Check that _blockExpiration is for future block
        require(_blockExpiration > block.number, "Invalid block expiration!");
        // Check that _premium is a valid number
        require(_premium > 0, "Invalid premium!");
        // Check that _strikePrice is a valid number
        require(_strikePrice > 0, "Invalid strike price!");

        // Create option
        Option memory _option = Option(_asset, msg.sender, address(0), _blockExpiration, addressNonce[msg.sender], _premium, _strikePrice, 0);
        // Create hash for option
        bytes32 _optionHash = keccak256(abi.encode(_option));
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
        require(_option.blockexpiration != 0, "This option does not exist!");
        // Check premium * 100 is equal to eth sent
        require(msg.value == _option.premium * 100, "Incorrect amount sent!");
        // Check option does not already have holder
        require(_option.holder == address(0), "This option has already been bought!");

        // Set holder directly in storage
        openOptions[_optionHash].holder = msg.sender;
        // Send eth to writer
        payable(_option.holder).transfer(msg.value);
        // Emit option buy
        emit OptionBought(_optionHash);
    }

    function approveOptionTransfer(bytes32 _optionHash, address _newBuyer, uint256 _price) public override {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockexpiration != 0, "This option does not exist!");
        // Check that current holder is calling this option
        require(msg.sender == _option.holder, "You are not the current holder!");

        // Set holderSellPrice for option
        openOptions[_optionHash].holderSellPrice = _price;
        // Add _newBuyer to approved addresses
        approvedAddress[_optionHash] = _newBuyer;
    }

    function transferOption(bytes32 _optionHash) public payable override {
        // Check that msg.sender has permission
        require(approvedAddress[_optionHash] == msg.sender, "You are not authorized!");
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockexpiration != 0, "This option does not exist!");
        // Check that msg.value is equal to holder's sell price
        require(_option.holderSellPrice == msg.value, "Incorrect amount sent!");

        // Change option holder
        openOptions[_optionHash].holder = msg.sender;
        // Delete approved address
        delete approvedAddress[_optionHash];

        // Send ETH to past holder
        payable(_option.holder).transfer(msg.value);
    }

    function exerciseOption(bytes32 _optionHash) public payable override {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Check that option exists
        require(_option.blockexpiration != 0, "This option does not exist!");
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
        payable(_option.writer).transfer(msg.value);
    }

    function refund(bytes32 _optionHash) public override {
        // Fetch option from storage and check if it is valid
        Option memory _option = openOptions[_optionHash]; 
        // Check that option is past block expiration or that no buyer has been assigned
        require(block.number > _option.blockexpiration || _option.holder == address(0), "You are not able to be refunded!");
        // Check that msg.sender is the option writer
        require(msg.sender == _option.writer, "You are not the option writer!");

        // Send 100 tokens back to seller
        IERC20 _token = IERC20(_option.asset);
        _token.transfer(msg.sender, 100);

        // Delete option from storage
        delete openOptions[_optionHash];
        delete approvedAddress[_optionHash];
    }

    function getOptionDetails(bytes32 _optionHash) public view override returns(address, address, address, uint64, uint32, uint256, uint256, uint256) {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Return option as tuple
        return (_option.asset, _option.writer, _option.holder, _option.blockexpiration, _option.sellerNonce, _option.premium, _option.strikePrice, _option.holderSellPrice);
    }
}