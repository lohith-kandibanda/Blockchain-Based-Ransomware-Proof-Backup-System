require("@nomiclabs/hardhat-waffle");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.21",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    sepolia: {
      url: "https://sepolia.infura.io/v3/8c37b79be49f41a191dc92f402e45107", // your Infura Sepolia URL
      accounts: ["c981edeef0998aff8eae05b41ff729238e02937dc0d90774d979fc1cc83b48b9"]
    }
  }
};
