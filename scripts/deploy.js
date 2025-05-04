const hre = require("hardhat");

async function main() {
  const BackupContract = await hre.ethers.getContractFactory("BackupContract");
  const contract = await BackupContract.deploy();
  await contract.deployed(); // ✅ this is correct for your setup
  console.log("BackupContract deployed to:", contract.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
