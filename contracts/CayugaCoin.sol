// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./ERC20.sol";

contract CayugaCoin is ERC20 {

    constructor(string memory _name, string memory _symbol) ERC20(_name, _symbol) {
        // Mint 10,000 tokens to msg.sender
        uint256 _tokens = 100000;
        _mint(msg.sender, _tokens * 10**18);
    }

}