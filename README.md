# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

This branch (`develop`) is for registering an asset with the Ocean Protocol Squid API.

You can find a live version of the app (no Ocean asset registration, `master` branch) at `159.69.202.132:4200`.

This is a deployable version. For the local deployment-only version, switch to the `local_deployment` branch.


## Requirements

- Python 3.6+ + python3-dev on Linux
- Pip3 9.0+
- GCC
- Node 8.10+
- NPM 3.5+
- One line install of the above on Ubuntu 18.04+:
    ```
    sudo apt install build-essential python3-dev python3-pip nodejs npm
    ```
- Angular CLI 6.2+
  - `sudo npm install -g @angular/cli`
- Yarn 1.10+
   - Debian-based Linux install:
      ```
      curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
      echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
      sudo apt-get update && sudo apt-get install yarn
      ```
### Asset Registration

- If on mac, gnu-sed: `brew install --with-default-names gnu-sed`


## Architecture

![Architecture Diagram](/doc/OceanHaja.png)


## How to use

Install dependencies:
```
pip3 install --upgrade setuptools
cd backend
pip3 install -r requirements.txt
npm install
cd ../frontend
yarn install --pure-lockfile
```

Make sure H2O-Host is running so that the database is available through IPFS. Without a provider of the database, it cannot be replicated.


### Running

#### Quickstart for all components

```
./launch
```

Hard errors will need a restart of the components that exited (typically backend, restart with `./backend/run`).

#### Running components individually

You'll need a running instance of Ocean Protocol. You can start an instance with H2O:
```
cd backend
docker-compose -f ./docker/docker-compose.yml up
```
The blockchain is ready once you see the output:
```
keeper-contracts_1  | eth_getFilterLogs
keeper-contracts_1  | eth_getFilterLogs
keeper-contracts_1  | eth_getFilterLogs
...
```
Local/testnet use can be specified with environment variables as usual with Ocean Protocol.

Next, open two terminal windows, one for back-end and one for front-end. You can run the tasks in a single window using `screen` or `bg` if you'd like.

In one terminal window:
```
./backend/run
```
In the other:
```
./frontend/run
```

Interact with the app in your browser at `0.0.0.0:4200`.


### Deployment

This deploys the app at your public IP. You must allow port 4200 and 8081.

The app is currently deployed using a Werkzeug dev server. This is not safe for production. If you want to go production-ready, use a WSGI HTTP server like [gunicorn](https://gunicorn.org/). When ready, the app will be switched to this.

To run:
```
screen
./backend/run
```
Press `CTRL` + `A`, then `CTRL` + `D`.

Next:
```
screen
./frontend/run
```
Wait a few seconds until you see `webpack: Compiled successfully.`

Press `CTRL` + `A`, then `CTRL` + `D`.

You can now close the terminal window. The app will continue to run.


## Roadmap

1. Hosting from H2O app
 - OrbitDB on IPFS.
 - Azure (possibly wrapper).
2. Make UI in line with Outlier Ventures branding.
3. Containerise.
4. Regulatory & publish.


## Useful info

Kovan addresses for manual `config.ini`:
```
market.address = 0xb8277FC2A46C11235775BEC194BD8C12ed92343C
auth.address = 0xfA65f2662224Dd340a2dea0972E70BA450E94e3C
token.address = 0x656f2Ab5D4C4bC2D5821fd959B083fd50273C2f1
```
