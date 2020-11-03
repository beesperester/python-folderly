""" Application module. """

__version__ = "0.1"
__author__ = "Bernhard Esperester"

# system
import json
import re

from os.path import dirname, basename

from fs.copy import copy_file_if_newer
from fs.osfs import OSFS

from slugify import slugify

# pylib
from pylib.utilities.util_config import Config
from pylib.extensions.ext_dict import add_node
from pylib.extensions.ext_fs import assert_fs
from pylib.extensions.ext_hash import \
    file_sha256, \
    hash_path
from pylib.extensions.ext_string import replace

# folderly
from folderly.constants import \
    HOME_PATH, \
    APP_CONFIG, \
    TEMPLATES_CONFIG

def _file_hash_path(file_hash):
    return hash_path(file_hash, 2, 1)

def _template_path(name, version, author):
    return "/".join([slugify(author), name, version])

def _unpack_template(resources_fs, template, destination_fs):
    for node, value in template.iteritems():
        if isinstance(value, dict):
            node_fs = assert_fs(destination_fs.getsyspath(unicode(node)))

            _unpack_template(resources_fs, value, node_fs)
        else:
            file_hash_path = _file_hash_path(value)

            copy_file_if_newer(resources_fs, file_hash_path, destination_fs, node)

class Folderly(object):

    def __init__(self, filesystem, **kwargs):
        """ Initialize folderly.

        Args:
            filesystem (fs)
        """

        config_path = u"config.json"
        config = {
            "templates": []
        }

        self._folderly_fs = assert_fs(filesystem.getsyspath(APP_CONFIG["path"]))
        self._templates_fs = assert_fs(self._folderly_fs.getsyspath(TEMPLATES_CONFIG["path"]))
        self.config = Config(self._folderly_fs, config_path, config)

    def pack(self, source, name, exclude=None):
        author = "Bernhard Esperester"
        version = "1.0"
        description = ""
        
        template_path = _template_path(name, version, author)
        
        source_fs = OSFS(source)
        destination_fs = assert_fs(self._templates_fs.getsyspath(unicode(template_path)))

        resources_fs = assert_fs(destination_fs.getsyspath(u"resources"))

        template = {}

        for path, info in source_fs.walk.info():
            # strip root node from path
            path = path[1:]

            # skip excluded
            if exclude:
                exclude_parts = exclude.split(",")

                matches = []

                for exclude_part in exclude_parts:
                    replace_dict = {
                        "*": ".*",
                        ".": "\.",
                        "/": "\/"
                    }
                    re_pattern = re.compile(replace(exclude_part, replace_dict), re.DOTALL)

                    if re.match(re_pattern, path):
                        matches.append(True)

                if True in matches:
                    continue

            if info.is_dir:
                if path:
                    add_node(template, path)
            else:                
                file_hash = file_sha256(source_fs.getsyspath(path))
                add_node(template, path, file_hash)

                file_hash_path = _file_hash_path(file_hash)

                hash_fs = assert_fs(resources_fs.getsyspath(unicode(dirname(file_hash_path))))

                copy_file_if_newer(source_fs, path, hash_fs, unicode(basename(file_hash_path)))

        folderly_dict = {
            "author": author,
            "version": version,
            "name": name,
            "description": description,
            "template": template
        }

        with destination_fs.open(TEMPLATES_CONFIG["config_path"], "w") as file_handle:
            file_handle.write(unicode(json.dumps(folderly_dict, indent=4)))

    def unpack(self, destination, name):
        author = "Bernhard Esperester"
        version = "1.0"
        
        template_path = _template_path(name, version, author)

        destination_fs = assert_fs(destination)
        template_fs = self._templates_fs.opendir(unicode(template_path))
        resources_fs = template_fs.opendir(u"resources")

        if template_fs.isfile(TEMPLATES_CONFIG["config_path"]):
            with template_fs.open(TEMPLATES_CONFIG["config_path"], "r") as file_handle:
                try:
                    data = json.loads(file_handle.read())

                    _unpack_template(resources_fs, data["template"], destination_fs)
                except ValueError:
                    pass

def init():
    """ Initialize application and return instance of Folderly.

    Returns:
        Folderly
    """

    # home_fs = OSFS(HOME_PATH)

    # if not home_fs.isdir(APP_CONFIG["path"]):
    #     home_fs.makedir(APP_CONFIG["path"])

    # folderly_fs = home_fs.opendir(APP_CONFIG["path"])

    return Folderly(OSFS(HOME_PATH))

