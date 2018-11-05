# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

You can find a live version of the app at `159.69.202.132:4200`.

Publishing assets requires an Azure Storage account.
Proof-of-concept OrbitDB hosting can be found in the `backend` folder, see `app.py` and `host.js`.


## Architecture

![Architecture Diagram](/doc/OceanHaja.png)


## Getting started

H2O runs on Linux and MacOS with command line tools (type `gcc` in terminal to install).

You'll need Docker and Docker Compose 1.22. Docker Compose 1.23 and later uses container naming incompatible with Ocean Protocol - once Ocean roll out a fix, we'll update here.

### Install
```
sudo ./install
```
If you encounter any install problems, there is a full requirements list at the bottom of this file for manual installations.

### Run

#### Quickstart for all components

Start an instance of Ocean Protocol:
```
./ocean
```
This will launch Ocean in a `screen` session. Once the blockchain is ready, you will see repeat output `keeper-contracts_1  | eth_getFilterLogs`, at which point you can detach from the screen with `CTRL` + `A`, `CTRL` + `D`.

Next, launch H2O:
```
./launch
```
The backend and frontend are started in separate `screen` tabs. You can switch between them using `CTRL` + `A`, `SHIFT` + `'`.

Hard errors will need a restart of the components that exited (this will typically be backend, restart it with `cd backend && ./run`).

You can view the app at `0.0.0.0:4200`.

#### Running components individually

Start an instance of Ocean Protocol:
```
./ocean
```
This will launch Ocean in a `screen` session. Once the blockchain is ready, you will see repeat output `keeper-contracts_1  | eth_getFilterLogs`, at which point you can detach from the screen with `CTRL` + `A`, `CTRL` + `D`.

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

To deploy use the `live` branch.
Expose ports `4200` and `8545`.
The app will be accessible at `[YOUR_PUBLIC_IP]:4200`.
The code has not yet been audited – deploy at your own risk.

The app is currently deployed using a Werkzeug dev server. This is not safe for production. If you want to go production-ready, use a WSGI HTTP server like [gunicorn](https://gunicorn.org/). When ready, the app will be switched to this.


## Roadmap

1. Make UI in line with Outlier Ventures branding (0.9.6).
2. Containerise (0.9.7).
3. Regulatory & publish (1.0.0).


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
- Docker & Docker Compose 1.22
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
