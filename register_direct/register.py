from squid_py.ocean_contracts import OceanContracts
from squid_py.consumer import register

import json





json_dict = {"publisherId": "0x1",
             "base": {
                 "name": "UK Weather information 20111",
                 "description": "Weather information of UK including temperature and humidity",
                 "size": "3.1gb",
                 "author": "Met Office",
                 "license": "CC-BY",
                 "copyrightHolder": "Met Office",
                 "encoding": "UTF-8",
                 "compression": "zip",
                 "contentType": "text/csv",
                 "workExample": "stationId,latitude,longitude,datetime,temperature,humidity\n"
                                "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
                 "contentUrls": ["https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf"],
                 "links": [
                     {"sample1": "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded-land-obs-daily/"},
                     {
                         "sample2": "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded-land-obs-averages-25km/"},
                     {"fieldsDescription": "http://data.ceda.ac.uk/badc/ukcp09/"}
                 ],
                 "inLanguage": "en",
                 "tags": "weather, uk, 2011, temperature, humidity",
                 "price": 10,
                 "type": "dataset"
             },
             "curation": {
                 "rating": 0,
                 "numVotes": 0,
                 "schema": "Binary Votting"
             },
             "additionalInformation": {
                 "updateFrecuency": "yearly"
             },
             "assetId": "001"
             }






test_consumable = json.dumps(json_dict)

# OceanContracts is the new name for OceanContractsWrapper
ocean = OceanContracts(host = 'http://localhost',
                       port = 8545,
                       config_path = 'config.ini')

# TODO: fill in JSON data as specified in contracts

register(publisher_account = ocean.web3.eth.accounts[1],
         provider_account = ocean.web3.eth.accounts[0],
         price = 10,
         ocean_contracts_wrapper = ocean,
         json_metadata = test_consumable)
