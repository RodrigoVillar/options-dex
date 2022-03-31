pragma solidity 0.8.0;

/*
Interface for OptionsDex
*/
interface IOptionsDex {

    function createOption(address _asset, uint256 _premium, uint256 _strikePrice, uint64 _blockExpiration) external;

    function buyOption(bytes32 _optionHash) payable external;

    function approveOptionTransferHolder(bytes32 _optionHash, address _newBuyer, uint256 _price) external;

    function transferOptionHolder(bytes32 _optionHash) payable external;

    function approveOptionTransferWriter(bytes32 _optionHash, uint256 _price, address _newWriter) external;

    function transferOptionWriter(bytes32 _optionHash) payable external;

    function exerciseOption(bytes32 _optionHash) payable external;

    function refund(bytes32 _optionHash) external;

    function getOptionDetails(bytes32) external view returns (address, address, address, uint64, uint32, uint256, uint256, uint256, uint256);

}