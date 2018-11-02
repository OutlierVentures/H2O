# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

This branch (`develop`) is for registering an asset with the Ocean Protocol Squid API.

You can find a live version of the app (no Ocean asset registration, `master` branch) at `159.69.202.132:4200`.

This is a deployable version. For the local deployment-only version, switch to the `local_deployment` branch.

## Architecture

![Architecture Diagram](/doc/OceanHaja.png)


## Getting started

### Install
```
./install
```
If you encounter errors, try running with `sudo`. If you still have problems, there is a full requirements list at the bottom of this file for manual installations.

### Run

#### Quickstart for all components

```
./launch
```
Ocean Protocol, backend and frontend are started in separate `screen` tabs. You can switch between them using `CTRL` + `A`, `SHIFT` + `'`.

Hard errors will need a restart of the components that exited (this will typically be backend, restart it with `cd backend && ./run`).

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

Next, open two terminal windows, one for backend and one for frontend. You can run the tasks in a single window using `screen` or `bg` if you'd like.

In one terminal window:
```
cd backend
./run
```
In the other:
```
cd frontend
./run
```

Interact with the app in your browser at `0.0.0.0:4200`.


### Deployment

This deploys the app at your public IP. You must allow port 4200 and 8081.

The app is currently deployed using a Werkzeug dev server. This is not safe for production. If you want to go production-ready, use a WSGI HTTP server like [gunicorn](https://gunicorn.org/). When ready, the app will be switched to this.

To run:
```
screen
cd backend
./run
```
Press `CTRL` + `A`, then `CTRL` + `D`.

Next:
```
screen
cd frontend
./run
```
Wait a few seconds until you see `webpack: Compiled successfully.`

Press `CTRL` + `A`, then `CTRL` + `D`.

You can now close the terminal window. The app will continue to run.


## Roadmap

1. Hosting from H2O app (0.9.5)
 - OrbitDB on IPFS.
 - Azure (possibly wrapper).
2. Make UI in line with Outlier Ventures branding (0.9.6).
3. Containerise (0.9.7).
4. Regulatory & publish (1.0.0).


## Useful info

Kovan addresses for manual `config.ini`:
```
market.address = 0xb8277FC2A46C11235775BEC194BD8C12ed92343C
auth.address = 0xfA65f2662224Dd340a2dea0972E70BA450E94e3C
token.address = 0x656f2Ab5D4C4bC2D5821fd959B083fd50273C2f1
```

## Full requirements list

If you encounter errors with the install script, here is a full list of requirements:

H2O runs on Linux and MacOS.

- MacOS: command line tools, Homebrew & `gnu-sed`
- Docker & Docker Compose
- Python 3 (`python3-dev` on Linux)
- Pip3
- GCC 4+
- Node 8+
- NPM 3+
- Angular CLI 6+
- Yarn 1.10+
- Finally, install dependencies:
    ```
    pip3 install --upgrade setuptools
    cd backend
    pip3 install -r requirements.txt
    npm install
    cd ../frontend
    yarn install --pure-lockfile
    ```
