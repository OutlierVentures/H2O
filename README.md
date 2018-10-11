# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

### Requirements

- Docker, Docker Compose
- Node.js, Yarn, Angular CLI
- Python, pip


### Architecture

![Architecture Diagram](/doc/OceanHaja.png)


### Build

```
docker-compose build
```


### Run

```
docker-compose up
```

### Roadmap

1. Stabilise closing of IPFS/OrbitDB connection
2. Link before/after clustering to flask endpoints
3. Add user interaction (import data, train on data buttons)
4. Clean up front end

Enhancements:
1. Pass ML output in through Flask endpoint as JSON object and draw in JS.
