# Squid

This is functionality that will be integrated with H2O/backend.

The following instructs how to run the Ocean asset registration independently.

## Installing

```
brew install --with-default-names gnu-sed
pip3 install -r requirements_dev.txt
```


## Running

You must set the required contract addresses in your `config.ini` file.
For Kovan:
KOVAN ADDRESSES

Terminal 1:
```
docker-compose -f ./docker/docker-compose.yml up
```
Terminal 2:
```
python3 register.py
```
