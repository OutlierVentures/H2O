# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

### Requirements

- Docker, Docker Compose
The following will be installed automatically:
- Node.js, Yarn, Angular CLI
- Python, pip, Flask, scikit-learn

### Architecture

![Architecture Diagram](/doc/OceanHaja.png)

### Run

```
docker-compose up
```

### Roadmap

1. Import OrbitDB wireframes
2. Find clusterable dataset
3. Put data in OrbitDB docs type database
4. Host OrbitDB docs database on IPFS and import with `replicate`
5. Write Python ML model to cluster data
6. Clean up front end
