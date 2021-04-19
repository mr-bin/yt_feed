import os
import yaml
import json
import logging
import collections

from yaml.loader import SafeLoader


class CustomLoggerClass(logging.Logger):
    _process_aware = True  # this is to prevent overwriting of basic logger class by celery

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """

        if extra:
            message = '{} -- {}'.format(msg, json.dumps(extra))
        else:
            message = msg

        rv = logging.LogRecord(name, level, fn, lno, message, args, exc_info, func,
                               sinfo)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        return rv


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


main_config_path = os.environ.get('CONFIG_PATH')
with open(main_config_path, 'r') as f:
    logs_path = os.environ.get('LOG_PATH', '')
    config_text = f.read().replace('__LOG_PATH__', logs_path)
    main_config = yaml.load(config_text, Loader=SafeLoader)

config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'etc', 'config.yaml')
with open(config_path, 'r') as f:
    logs_path = os.environ.get('LOG_PATH', '')
    config_text = f.read().replace('__LOG_PATH__', logs_path)
    base_config = yaml.load(config_text, Loader=SafeLoader)

config = update(base_config, main_config)
logging.setLoggerClass(CustomLoggerClass)
