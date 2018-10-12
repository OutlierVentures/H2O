# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

### Requirements

- Node
- Yarn
- Angular CLI
- Python
- Pip


### Architecture

![Architecture Diagram](/doc/OceanHaja.png)


### Run

Install dependencies:
```
cd backend
pip3 install -r requirements.txt
npm install
cd ../frontend
yarn install --pure-lockfile
```

Make sure H2O-Host is running so that the database is available through IPFS. Without a provider of the database, it cannot be replicated.

To run, open two terminal windows, one for back-end and one for front-end.

In one:
```
cd backend
python3 app.py
```
In the other:
```
cd frontend
yarn start
```

Interact with the app in your browser at `localhost:4200`.


### Roadmap

1. Deploy at a publicly accessible URL.
