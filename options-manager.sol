/*
Notes: if Option does not exist in mapping, then all fields will simply equal default value
(ex. 0, "", etc.)

SMART CONTRACT CURRENTLY VULNERABLE TO FALLBACK FUNCTIONS!
*/
pragma solidity 0.8.0;

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


contract OptionsDEX {

    struct Option {
        // ERC-20 address
        address asset;
        // Contract seller
        address seller;
        // Contract buyer
        address buyer;
        // Option valid up until blockExpiration
        uint128 blockExpiration;
        // Premium per token (in Wei)
        uint128 premium;
        // Right to buy token at strikePrice (in Wei)
        uint128 strikePrice;
        // Nonce to prevent identical transactions
        uint128 sellerNonce;
        // Whether a buyer is assigned to the option
        uint128 purchased;
    }

    uint64 constant quantity = 100;
    mapping(bytes32 => Option) private openOptions;
    mapping(address => uint128) private accountNonce;
    mapping(address => mapping(bytes32 => bool)) private allowances;
    mapping (bytes32 => uint128) private transferPrice;

    event OptionCreated(address indexed seller, bytes32 indexed optionHash);
    event OptionDeleted(bytes32 indexed optionHash);
    event OptionBought(bytes32 indexed optionHash);

    function createOption(address _asset, uint128 _premium, uint128 _strikePrice, uint128 _blockExpiration) public {
        // Enforce preconditions
        require(_blockExpiration > block.number, "Invalid block expiration date!");

        // Create Option
        Option memory createdOption = Option(_asset, msg.sender, address(0), _blockExpiration, _premium, _strikePrice, accountNonce[msg.sender], 0);
        bytes32 hsh = keccak256(abi.encode(createdOption));

        // Add option to state
        openOptions[hsh] = createdOption;
        // Increase account nonce to prevent two identical options from having same hash
        accountNonce[msg.sender] += 1;

        // Create ERC20 object
        IERC20 token = IERC20(_asset);
        // Transfer tokens to smart contract
        token.transferFrom(msg.sender, address(this), quantity);

        // Notify blockchain about new option
        emit OptionCreated(msg.sender, hsh);
    }

    /*
    Function related to first time purchase of option
    */
    function buyOption(bytes32 _optionHash) payable public {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Checking if option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check premium * 100 = eth sent
        require(msg.value == _option.premium * quantity, "Incorrect amount sent!");

        // Set buyer in option
        _option.buyer = msg.sender;
        // Set purchased value
        _option.purchased = 1;
        // Send eth to seller
        payable(_option.seller).transfer(msg.value);
        // Emit event
        emit OptionBought(_optionHash);
    }

    /* 
    Function related to approving option transfer from buyer A to buyer B, with buyer A
    intended to call this function before buyer B calls transferOption()
    */
    function approveOptionTransfer(bytes32 _optionHash, address _newBuyer, uint128 _price) public {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Checking if option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check if msg.sender is buyer
        require(_option.buyer == msg.sender, "You are not the current buyer of the option!");

        // Approve new buyer
        allowances[_newBuyer][_optionHash] = true;
        // Set new price in transferPrice
        transferPrice[_optionHash] = _price;
    }

    /*
    Function related to tranfering option from buyer A to buyer B, with buyer B calling
    this function to commit the transfer
    */
    function transferOption(bytes32 _optionHash) payable public {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Checking if option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check if msg.sender has approval
        require(allowances[msg.sender][_optionHash], "You don't have permission to recieve this option");

        // Check if buyer sent correct amount
        require(msg.value == transferPrice[_optionHash], "Incorrect amount of eth sent!");
        // Send eth to buyer A
        payable(_option.buyer).transfer(msg.value);
        // Set new buyer of option
        openOptions[_optionHash].buyer = msg.sender;


    }

    function exerciseOption(bytes32 _optionHash) payable public {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Checking if option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check if msg.sender is buyer
        require(_option.buyer == msg.sender, "You are not the current buyer of the option!");
        // Check if amount sent is correct
        require(msg.value == _option.strikePrice * 100, "Incorrect amount of eth sent!");

        // Send eth to seller
        payable(_option.seller).transfer(msg.value);
        // Delete option from storage
        delete transferPrice[_optionHash];
        delete openOptions[_optionHash];


    }

    function refund(bytes32 _optionHash) public {
        // Fetch option from storage
        Option memory _option = openOptions[_optionHash];
        // Checking if option exists
        require(_option.blockExpiration != 0, "This option does not exist!");
        // Check msg.sender is the option seller
        require(msg.sender == _option.seller, "Not the seller!");
        // If no buyer or past block expiration date, then seller can get tokens back
        require(_option.buyer == address(0) || _option.blockExpiration > block.number, "Criteria to sell not met!");

        // Send tokens back to seller
        IERC20 token = IERC20(_option.asset);
        token.transfer(msg.sender, quantity);

        // Delete option from openOptions
        delete openOptions[_optionHash];

        // Emit event
        emit OptionDeleted(_optionHash);
    }



}