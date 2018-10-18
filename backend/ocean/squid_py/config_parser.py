import os
import site
import configparser
import logging


def load_config_section(file_path, section):
    try:
        assert file_path and os.path.exists(file_path), 'config file_path is required.'
        config = parse_config(file_path, section)
        return config
    except Exception:
        logging.warning("You are not providing a valid configuration.")
        return None


def parse_config(file_path, section):
    """Loads the configuration file given as parameter"""
    config_parser = configparser.ConfigParser()
    config_parser.read(file_path)
    config_dict = {}
    options = config_parser.options(section)
    for option in options:
        try:
            config_dict[option] = config_parser.get(section, option)
            if config_dict[option] == -1:
                logging.info("skip: %s" % option)
        except Exception as err:
            logging.error("error on %s!" % option)
            logging.error("exception on %s" % str(err))
            config_dict[option] = None
    return config_dict


def get_contracts_path(conf):
    try:
        if conf is not None and 'contracts.folder' in conf:
            return conf['contracts.folder']
        elif os.getenv('VIRTUAL_ENV') is not None:
            return "%s/contracts" % (os.getenv('VIRTUAL_ENV'))
        else:
            return "%s/contracts" % (site.PREFIXES[0])
    except Exception as e:
        return e
