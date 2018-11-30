const HDWalletProvider = require('truffle-hdwallet-provider')

provider = new HDWalletProvider(process.env.KOVAN_NMEMORIC, `https://kovan.infura.io/v3/${process.env.INFURA_TOKEN}`)

console.log(provider.addresses[0])

process.exit()