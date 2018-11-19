
class AdditionalInfoMeta(object):
    KEY = 'additionalInfo'
    VALUES_KEYS = (
        "updateFrequency",
        "structuredMarkup"
    )
    REQUIRED_VALUES_KEYS = tuple()
    EXAMPLE = {
        "updateFrequency": "yearly",
        "structuredMarkup": [
            {
                "uri": "http://skos.um.es/unescothes/C01194/jsonld",
                "mediaType": "application/ld+json",
            },
            {
                "uri": "http://skos.um.es/unescothes/C01194/turtle",
                "mediaType": "text/turtle",
            },
        ],
    }


class CurationMeta(object):
    KEY = 'curation'
    VALUES_KEYS = (
        "rating", "numVotes", "schema"
    )
    REQUIRED_VALUES_KEYS = tuple()
    EXAMPLE = {
        "rating":   0.93,
        "numVotes": 123,
        "schema":   "Binary Voting",
    }


class MetadataBase(object):
    KEY = 'base'
    VALUES_KEYS = {
        'name',
        'type',
        'description',
        'size',
        'dateCreated',
        'author',
        'license',
        'copyrightHolder',
        'encoding',
        'compression',
        'contentType',
        'workExample',
        'links',
        'inLanguage',
        'tags',
        'price',
        "links",
        'contentUrls'
    }
    REQUIRED_VALUES_KEYS = {'name', 'type', 'description', 'contentUrls', 'contentType'}

    EXAMPLE = {
        'name':            "UK Weather information 2011",
        'type':            "dataset",
        'description':     "Weather information of UK including temperature and humidity",
        'size':            "3.1gb",
        'dateCreated':     "2012-10-10T17:00:000Z",
        'author':          "Met Office",
        'license':         "CC-BY",
        'copyrightHolder': "Met Office",
        'encoding':        "UTF-8",
        'compression':     "zip",
        'contentType':     "text/csv",
        'workExample':     "423432fsd,51.509865,-0.118092,2011-01-01T10:55:11+00:00,7.2,68",
        'inLanguage':      "en",
        'tags':            "weather, uk, 2011, temperature, humidity",
        'price':           23,
        'contentUrls': [
            "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.zip",
            "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.zip",
        ],
        'links': [
            {
                "sample1": "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded-land-obs-daily/",
            },
            {
                "sample2": "http://data.ceda.ac.uk/badc/ukcp09/data/gridded-land-obs/gridded-land-obs-averages-25km/",
            },
            {
                "fieldsDescription": "http://data.ceda.ac.uk/badc/ukcp09/",
            },

        ],
    }


class Metadata(object):
    REQUIRED_SECTIONS = {MetadataBase.KEY, }
    MAIN_SECTIONS = {
        MetadataBase.KEY: MetadataBase,
        CurationMeta.KEY: CurationMeta,
        AdditionalInfoMeta.KEY: AdditionalInfoMeta
    }

    @staticmethod
    def validate(metadata):
        # validate required sections and their sub items
        for section_key in Metadata.REQUIRED_SECTIONS:
            if section_key not in metadata or not metadata[section_key] or not isinstance(metadata[section_key], dict):
                return False

            section = Metadata.MAIN_SECTIONS[section_key]
            section_metadata = metadata[section_key]
            for subkey in section.REQUIRED_VALUES_KEYS:
                if subkey not in section_metadata or not section_metadata[subkey]:
                    return False

        return True

    @staticmethod
    def get_example():
        example = dict()
        for section_key, section in Metadata.MAIN_SECTIONS.items():
            example[section_key] = section.EXAMPLE

        return example
