# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

You can find a live version of the app at `https://159.69.202.132`.

Publishing assets requires an Azure Storage account.
Proof-of-concept OrbitDB hosting can be found in `h2o/backend` folder, see `app.py` and `host.js`.

This app runs Squid-py 0.2.5. The squid component will be updated with stable releases.

## Architecture

![Architecture Diagram](/images/OceanHaja.png)


## Getting started

H2O runs on Linux and MacOS with XCode + command line tools.

You'll need Docker and Docker Compose.

### Quick run
```
./launch
```

### Development

Dev mode runs H2O on your local machine instead of in a Docker container.

#### Install components

```
sudo ./dev_install
```
If you encounter any install problems, there is a full requirements list at the bottom of this file for manual installations.

#### Running components individually

Start an instance of Ocean Protocol:
```
cd ocean
./launch_ocean
```
You can add the option `kovan` to use the testnet contracts: `./start_ocean kovan`.

This will launch Ocean in a `screen` session. Once the blockchain is ready, you will see repeat output `keeper-contracts_1  | eth_getFilterLogs`, at which point you can detach from the screen with `CTRL` + `A`, `CTRL` + `D`.

Next, open two terminal windows, one for backend and one for frontend. You can run the tasks in a single window using `screen` or `bg` if you'd like.

In one terminal window:
```
cd h2o/backend
./run
```
In the other:
```
cd h2o/frontend
./run
```

Interact with the app in your browser at `0.0.0.0:4200`.


#### Deployment

*Containerisation + production server in development on the `deploy` branch.*

To deploy yourself (currently at your own risk, uses dev server), switch to the `live` branch.

Expose ports `4200` and `8545`.
The app will be accessible at `[YOUR_PUBLIC_IP]:4200`.
The code has not yet been audited – deploy at your own risk.

The `live` branch uses a Werkzeug dev server. This is not safe for production. If you want to go production-ready, use a WSGI HTTP server like [gunicorn](https://gunicorn.org/). Likewise, frontend runs an Angular dev server, which you will need to switch to a production server. This is currently in development on the `deploy` branch.


## Roadmap

1. Containerise and set up on production server (0.9.6).
2. Make UI in line with Outlier Ventures branding (0.9.7).
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

- MacOS: command line tools, Homebrew
- Linux: GCC 4+
- Docker & Docker Compose
- Python 3 (`python3-dev` on Linux)
- Pip3
- Node 8 (strictly version 8 - this is because of `node-gyp`)
- NPM 3
- Angular CLI 1+
- Yarn 1.10+
- Finally, install dependencies:
    ```
    pip3 install --upgrade setuptools
    pip3 install wheel
    cd backend
    pip3 install -r requirements.txt
    npm install orbit-db ipfs
    cd ../frontend
    yarn install --pure-lockfile
    ```
