const HDWalletProvider = require('truffle-hdwallet-provider')
const fs = require('fs')

publisher = new HDWalletProvider(process.env.KOVAN_NMEMORIC, `https://kovan.infura.io/v3/${process.env.INFURA_TOKEN}`)
address = publisher.addresses[0]
key = publisher.wallets[address]._privKey.toString('hex')
fs.writeFileSync('address', address);
console.log("\033[0;32mYour publisher address: \033[1;31m" + address + "\n\033[0;32mPrivate key: \033[1;31m" + key +
"\n\033[1;31mNever share your private key or commit it to Git.\n\033[0;32mAdd this account to a wallet of your choice with the private key, e.g. MetaMask.\033[0m")

process.exit()
