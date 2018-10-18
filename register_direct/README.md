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


## Asset structure

https://github.com/oceanprotocol/squid-py/blob/3a808bd29ebf24d28267faf518cbe9002016d9b5/tests/test_keeper.py

https://github.com/oceanprotocol/pleuston/blob/90247641e859e9ce4655d2d1cf8df1d083927408/src/mock/assets.js

https://github.com/oceanprotocol/provider/blob/67ee3192ab6fda5e726eda8e346da3468f75c716/tests/conftest.py
