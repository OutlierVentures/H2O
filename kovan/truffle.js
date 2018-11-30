const HDWalletProvider = require('truffle-hdwallet-provider')

publisher = new HDWalletProvider(process.env.KOVAN_NMEMORIC, `https://kovan.infura.io/v3/${process.env.INFURA_TOKEN}`)

module.exports = {
    networks: {
        // only used locally, i.e. ganache
        development: {
            host: 'localhost',
            port: 8545,
            // has to be '*' because this is usually ganache
            network_id: '*',
            gas: 6000000
        },
        // local testnet for generate coverage
        coverage: {
            host: 'localhost',
            // has to be '*' because this is usually ganache
            network_id: '*',
            port: 8555,
            gas: 0xfffffffffff,
            gasPrice: 0x01
        },
        // only used locally, i.e. docker
        ocean_poa_net_local: {
            host: process.env.POA_HOST,
            port: 8545,
            // poa from docker usually
            network_id: 0x2324,
            gas: 4500000,
            from: '0x00bd138abd70e2f00903268f3db08f2d25677c9e'
        },
        // new aws instance of POA
        ocean_poa_aws: {
            provider: () => new HDWalletProvider(process.env.POA_NMEMORIC, `http://52.1.94.55:8545`),
            network_id: 0x2323,
            gas: 6000000,
            gasPrice: 10000,
            from: '0x90eE7A30339D05E07d9c6e65747132933ff6e624'
        },
        // kovan testnet
        kovan: {
            provider: () => publisher,
            network_id: '42',
            from: publisher.addresses[0]
        }
    },
    compilers: {
        solc: {
            version: '0.4.25'
        }
    },
    solc: {
        optimizer: {
            enabled: true,
            runs: 200
        }
    }
}
