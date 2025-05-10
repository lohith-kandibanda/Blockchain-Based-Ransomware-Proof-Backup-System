// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BackupContract {
    struct Backup {
        string ipfsHash;
        uint timestamp;
        address owner;
        bytes32 fileHash; // ✅ Added for integrity check
    }

    mapping(string => Backup[]) private backups;

    event BackupStored(string indexed fileId, string ipfsHash, uint version, address indexed owner, bytes32 fileHash);

    // ✅ Updated: Accepts fileHash as parameter
    function storeBackup(string memory fileId, string memory ipfsHash, bytes32 fileHash) public {
        backups[fileId].push(Backup(ipfsHash, block.timestamp, msg.sender, fileHash));
        emit BackupStored(fileId, ipfsHash, backups[fileId].length - 1, msg.sender, fileHash);
    }

    // ✅ Updated: Returns fileHash too
    function getBackup(string memory fileId, uint version) public view returns (
        string memory, uint, address, bytes32
    ) {
        require(version < backups[fileId].length, "Invalid version");
        Backup memory b = backups[fileId][version];
        return (b.ipfsHash, b.timestamp, b.owner, b.fileHash);
    }

    function getVersionCount(string memory fileId) public view returns (uint) {
        return backups[fileId].length;
    }
}
