// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BackupContract {
    struct Backup {
        string ipfsHash;
        uint timestamp;
        address owner;
    }

    mapping(string => Backup[]) private backups;

    event BackupStored(string indexed fileId, string ipfsHash, uint version, address indexed owner);

    function storeBackup(string memory fileId, string memory ipfsHash) public {
        backups[fileId].push(Backup(ipfsHash, block.timestamp, msg.sender));
        emit BackupStored(fileId, ipfsHash, backups[fileId].length - 1, msg.sender);
    }

    function getBackup(string memory fileId, uint version) public view returns (string memory, uint, address) {
        require(version < backups[fileId].length, "Invalid version");
        Backup memory b = backups[fileId][version];
        return (b.ipfsHash, b.timestamp, b.owner);
    }

    function getVersionCount(string memory fileId) public view returns (uint) {
        return backups[fileId].length;
    }
}
