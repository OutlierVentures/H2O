const config = require('../config')
const fs = require('fs');
const IPFS = require('ipfs')
const OrbitDB = require('orbit-db')

const ipfsOptions = {
  start: true,
  EXPERIMENTAL: {
    pubsub: true,
  },
  config: {
    Addresses: {
      Swarm: [
        '/dns4/ws-star.discovery.libp2p.io/tcp/443/wss/p2p-websocket-star',
      ]
    },
  }
}

const ipfs = new IPFS(ipfsOptions)

ipfs.on('error', (e) => console.error(e))

ipfs.on('ready', async () => {

  const orbitdb = new OrbitDB(ipfs)

  const db = await orbitdb.open(config.address, { sync: true })
  await db.load()

  db.events.on('replicated', () => {

    let data = {
      "x": getArray(db, 'x'),
      "y": getArray(db, 'y'),
      "truth": getArray(db, 't')
    }
    fs.writeFileSync('data.json', JSON.stringify(data));

    /*
    orbitdb.disconnect()
    ipfs.stop(() => {})
    */
    
  })

})

function getArray(db, name) {

  return db.get(name)[0].array

}
