
class AdditionalInfoMeta(object):
    KEY = 'additionalInformation'
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
        'name':            "Ocean protocol white paper",
        'type':            "dataset",
        'description':     "Introduce the main concepts and vision behind ocean protocol",
        'size':            "1mb",
        'dateCreated':     "2012-10-10T17:00:000Z",
        'author':          "Ocean Protocol Foundation Ltd.",
        'license':         "CC-BY",
        'copyrightHolder': "Ocean Protocol Foundation Ltd.",
        'encoding':        "UTF-8",
        'compression':     "",
        'contentType':     "text/csv",
        'workExample':     "Text PDF",
        'inLanguage':      "en",
        'tags':            "data exchange sharing curation bonding curve",
        'price':           23,
        'contentUrls': [
            "https://testocnfiles.blob.core.windows.net/testfiles/testzkp.pdf"
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
            example[section_key] = section.EXAMPLE.copy()

        return example
