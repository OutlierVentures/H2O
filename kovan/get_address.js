const HDWalletProvider = require('truffle-hdwallet-provider')
const fs = require('fs')

publisher = new HDWalletProvider(process.env.KOVAN_NMEMORIC, `https://kovan.infura.io/v3/${process.env.INFURA_TOKEN}`)
address = publisher.addresses[0]
fs.writeFileSync('address', address);
console.log("\033[1;32mYour publisher address:\n" + address + "\033[0m")

process.exit()