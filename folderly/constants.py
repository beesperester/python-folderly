""" Constants module. """

HOME_PATH = u"~"

APP_CONFIG = {
    "path": u".folderly",
    "config_path": u"config.json"
}

TEMPLATES_CONFIG = {
    "path": u"templates",
    "config_path": u"folderly.json"
}

TEMPLATE_PACKAGE_DEFAULT = {
    "name": "",
    "author": "",
    "version": "1.0",
    "description": "",
    "license": "",
    "template": {}
}

TEMPLATE_PACKAGE_RULES = {
    "name": [
        "required",
        "regex:^[a-zA-Z-_]+$",
        "min-length:2"
    ],
    "author": [
        "required",
        "min-length:2"
    ],
    "description": [
        "min-length:2"
    ],
    "license": [
        "required"
    ],
    "version": [
        "required"
    ]
}