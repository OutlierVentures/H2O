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
market.address = 0xb8277FC2A46C11235775BEC194BD8C12ed92343C
auth.address = 0xfA65f2662224Dd340a2dea0972E70BA450E94e3C
token.address = 0x656f2Ab5D4C4bC2D5821fd959B083fd50273C2f1

Terminal 1:
```
docker-compose -f ./docker/docker-compose.yml up
```
Terminal 2:
```
python3 register.py
```
