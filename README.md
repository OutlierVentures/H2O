# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

This branch (`develop`) is for registering an asset with the Ocean Protocol Squid API.

For now, asset registration is executed independently (i.e. separate to `app.py`). The two will soon be merged into a single app.

You can find a live version of the app (no Ocean asset registration, `master` branch) at `159.69.202.132:4200`.

This is a deployable version. For the local deployment-only version, switch to the `local_deployment` branch.


## Requirements

- Python 3.6+
- Pip3 9.0+
- Node 8.10+
- NPM 3.5+
- Angular CLI 6.2+
  - `sudo npm install -g @angular/cli`
- Yarn 1.10+
   - Linux install:
      ```
      curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
      echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
      sudo apt-get update && sudo apt-get install yarn
      ```
### Asset Registration

- If on mac, gnu-sed: `brew install --with-default-names gnu-sed`


## Architecture

![Architecture Diagram](/doc/OceanHaja.png)


## Run

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

### Asset registration

Asset registration is functional but a bit clunky while it is being integrated with the UI.

If you do want to try it out, navigate to `backend/ocean` in two terminal windows.

In one terminal window, start the Ocean Protocol blockchain:
```
docker-compose -f ./docker/docker-compose.yml up
```
Wait until you see the output `keeper-contracts_1  | eth_getFilterLogs`.

Next, fill in the contract addresses in the `config.ini` file (in the same `backend/ocean` folder) by searching for `OceanMarket:`, `OceanAuth:` and `OceanToken:` in this terminal window. Fortunately, `CTRL` + `F` works with most modern terminals.

Automatic parsing of these addresses will be added to H2O soon.

Once you've pasted the addresses in to `config.ini`, save the file. You can now register an asset with the `register.py` file. Feel free to fill in your own metadata, though sample content has been provided.

To register an asset, use the other terminal window in which you navigated to `backend/ocean`:
```
python3 register.py
```

You should get a confirmation of asset registration message in your terminal window.

The asset registration functionality will be added to `app.py` and be accessible with the H2O UI soon.


### Deployment

This deploys the app at your public IP. You must allow port 4200 and 8081.

The app is currently deployed using a Werkzeug dev server. This is not safe for production. If you want to go production-ready, use a WSGI HTTP server like [gunicorn](https://gunicorn.org/). When ready, the app will be switched to this.

To run:
```
screen
cd backend
python3 app.py
```
Press `CTRL` + `A`, then `CTRL` + `D`.

Next:
```
screen
cd frontend
yarn start
```
Wait a few seconds until you see `webpack: Compiled successfully.`

Press `CTRL` + `A`, then `CTRL` + `D`.

You can now close the terminal window. The app will continue to run.


### Development

You can run the back and front end in separate terminals for easier development.

Open two terminal windows.

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

Interact with the app in your browser at `0.0.0.0:4200`.


## Roadmap

1. Parse Ocean Protocol blockchain configuration addresses automatically.
2. Add asset registration UI.
3. Add automatic setup of asset hosting within H2O and integrate this with the asset registration UI.
4. Migrate contracts to Kovan. Kovan addresses:
      ```
      market.address = 0xb8277FC2A46C11235775BEC194BD8C12ed92343C
      auth.address = 0xfA65f2662224Dd340a2dea0972E70BA450E94e3C
      token.address = 0x656f2Ab5D4C4bC2D5821fd959B083fd50273C2f1
      ```
5. Make UI in line with Outlier Ventures branding.
6. Regulatory & publish.
