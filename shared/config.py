"""The shared logging configuration that should be used in all parts of the application."""
import sys

logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(name)-25s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'stderr': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stderr,
        },
    },
    'loggers': {
        'urllib3': {'level': 'INFO', },
    },
    'root': {
        'handlers': ['stdout', ],
        'level': 'DEBUG',
    },
}
