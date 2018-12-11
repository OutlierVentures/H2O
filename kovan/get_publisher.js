const HDWalletProvider = require('truffle-hdwallet-provider')
const EthWalletLib = require('ethereumjs-wallet')
const fs = require('fs')
const prompt = require('password-prompt');

(async () => {

    pass = await prompt('\033[1;31mEnter password for keystore file: ', {
        method: 'hide'
    })

    publisher = new HDWalletProvider(process.env.KOVAN_NMEMORIC, `https://kovan.infura.io/v3/${process.env.INFURA_TOKEN}`)
    address = publisher.addresses[0]
    key = publisher.wallets[address]._privKey

    wallet = EthWalletLib.fromPrivateKey(key)
    v3 = wallet.toV3String(pass.toString())

    fs.writeFileSync('keystore.json', v3)
    fs.writeFileSync('address', address)
    fs.writeFileSync('pass', pass)

    console.log("\033[0;32mYour publisher address: \033[1;31m" + address + "\n\033[0;32mPrivate key: \033[1;31m" + key.toString('hex') +
    "\n\033[1;31mNever share your private key or commit it to Git.\n\033[0;32mAdd this account to a wallet of your choice, e.g. MetaMask.\nYou can do this with the private key above or a keystore JSON.\nA keystore file has been created in the kovan folder.\033[0m")

    publisher.engine.stop();

})()
.catch(error => console.log(error))
