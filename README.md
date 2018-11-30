# H2O: Haja to Ocean

<p align="center"><br/><br/><img src='/images/components.png' width='300px' /><br/><br/><b>Machine learning with OrbitDB & Ocean Protocol</b><br/><br/></p>

You can find a live version of the app at [h2o.apps.outlierventures.io](https://h2o.apps.outlierventures.io/home).

Publishing assets requires an Azure Storage account.
Proof-of-concept OrbitDB hosting can be found in `backend` folder, see `app.py` and `host.js`.

This app runs Squid-py 0.2.5.

## Architecture

### Dataflow

![Dataflow](/images/dataflow.png)

### Architecture diagram

![Architecture](/images/architecture.png)


## Getting started

H2O runs on Linux and MacOS with command line tools.

### Install components

```
sudo ./install
```
If you encounter any install problems, there is a full requirements list at the bottom of this file for manual installations.

### Running components

Start an instance of Ocean Protocol:
```
./launch_ocean
```

In another teminal window, launch H2O:
```
./launch_h2o
```

Interact with the app in your browser at `0.0.0.0:4200`.


### Using Kovan

See `README.md` in the `kovan` folder.


### Deployment

You can run an H2O client using nginx.

Move H2O to `/var/www/your-domain-name.example`.

You can quickly set up an nginx configuration using [nginxconfig.io](https://nginxconfig.io). 

*Set up HTTPS since users will be supplying an Azure storage key.*

*In no event shall Outlier Ventures, Outlier Ventures Operations, their employees, their associates or the authors of this software be liable to you or any third parties for any special, punitive, incidental, indirect or consequential damages of any kind, or any damages whatsoever, including, without limitation, those resulting from loss of use, data or profits, whether or not the aforementioned parties have been advised of the possibility of such damages, and on any theory of liability, arising out of or in connection with the use of this software.*

Get an instance of Ocean Protocol up and running.

In one screen session:
```
cd frontend
sudo ng build --watch --output-hashing=all
```
Output hashing is needed to prevent browsers loading their cached copies of the graphed datasets.

Point nginx to the `dist` folder `ng-build` produces (will be in `frontend` next to `src`).

In another:
```
cd backend
sudo python3 app.py
```

Disconnect from your screen sessions and H2O will continue to run.


## Full requirements list

If you encounter errors with the install script, here is a full list of requirements:

H2O runs on Linux and MacOS.

- MacOS: command line tools, Homebrew
- Linux: GCC 4+
- Python 3 (`python3-dev` on Linux)
- Pip3
- Node 8 (strictly version 8 - this is because of `node-gyp`)
- NPM 6+
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
