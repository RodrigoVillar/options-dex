pragma solidity 0.8.0;

/*
Interface for OptionsDex
*/
interface IOptionsDEX {

    function createOption(address _asset, uint96 _premium, uint96 _strikePrice, uint96 _blockExpiration) external;

    function buyOption(bytes32 _optionHash) payable external;

    function approveOptionTransferHolder(bytes32 _optionHash, address _newBuyer, uint128 _price) external;

    function transferOptionHolder(bytes32 _optionHash) payable external;

    function approveOptionTransferWriter(bytes32 _optionHash, address _newWriter, uint128 _price) external;

    function transferOptionWriter(bytes32 _optionHash) payable external;

    function exerciseOption(bytes32 _optionHash) payable external;

    function refund(bytes32 _optionHash) external;

    function getOptionDetails(bytes32) external view returns (address, uint96, address, uint96, address, uint96, uint128, uint128);

    function viewHolderApproval(bytes32 _optionHash) external view returns (address);

    function viewWriterApproval(bytes32 _optionHash) external view returns (address);

    receive() external payable;

}