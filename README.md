# H2O: Haja to Ocean

Machine learning in Nautilina with OrbitDB.

You can find a live version of the app at `159.69.202.132:4200`.

This is a deployable version. For the local deployment-only version, switch to the `local_deployment` branch.


### Requirements

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

### Architecture

![Architecture Diagram](/doc/OceanHaja.png)


### Run

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

#### Deployment

This deploys the app at your public IP. You must allow port 4200 and 8081.

The app is currently deployed using a Werkzeug dev server. This is not safe for production. If you want to go production-ready, use a WSGI HTTP server like [gunicorn](https://gunicorn.org/). When ready, the app will be switched to this.

To run:
```
cd backend
python3 app.py
```
Press `CTRL` + `Z`.
```
bg
```

Next:
```
cd frontend
yarn start
```
Wait a few seconds until you see `webpack: Compiled successfully.`

Press `CTRL` + `Z`.
```
bg
```
You can now close the terminal window. The app is running in the background.


#### Development

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

Interact with the app in your browser at `localhost:4200`.

