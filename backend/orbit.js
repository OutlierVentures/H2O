const config = require('./config.json')
const fs = require('fs')

if (!fs.existsSync('data.json')) {

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

    const db = await orbitdb.open(config.address)
    await db.load()

    db.events.on('replicated', async () => {
      try {
        let data = {
          "x": getArray(db, 'x'),
          "y": getArray(db, 'y'),
          "t": getArray(db, 't')
        }
        fs.writeFileSync('data.json', JSON.stringify(data));
        await orbitdb.disconnect()
        await ipfs.stop(() => {})
        process.exit()
      }
      catch(error) {
        // OrbitDB considers itself loaded before it is readable, catch this
        console.log('Loading OrbitDB...')
      }

    })

  })
  function getArray(db, name) {

    let entry = db.get(name)
    return entry[0].array

  }

}
