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

  const db = await orbitdb.open('/orbitdb/QmcHKBHmXmx3HHi1opqAVqF4E3qwwkmJPQ8CeVX4ybc4xJ/trainingdata', { sync: true })
  await db.load()

  db.events.on('replicated', () => {
    const value = db.get('01')
    console.log(value)
  })

})
