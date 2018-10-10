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


    x = db.get('x')[0].array
    console.log(x)
    //console.log(db.query((doc) => doc))
    /*
    let data = {
      x: db.get('x'),
      y: db.get('y'),
      truth: db.get('t')
    }
    console.log(data)
    */
    //TODO: WRITE TO JSON
    orbitdb.disconnect()
    ipfs.stop(() => {})

  })

})
