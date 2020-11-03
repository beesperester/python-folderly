""" Filesystem module. """

# system
import re

from fs.osfs import OSFS

# pylib
from pylib.utilities.util_structures import \
    DirectoryNode, \
    FileNode, \
    RootNode

from pylib.extensions.ext_hash import \
    file_sha256, \
    hash_path
from pylib.extensions.ext_string import \
    replace

def gather(source_path):
    """ Gather directories and files in source_path.

    Args:
        source_path (string)

    Returns:
        list
    """

    source_fs = OSFS(source_path)

    # root_node = RootNode()

    paths_list = []

    for path, info in source_fs.walk.info(namespaces=["details"]):
        # strip root node from path
        path = path[1:]

        if path:
            paths_list.append(path)

            # if info.is_dir:
            #     # add directory node from path
            #     root_node.add_directory_node(path)
            #     paths_list.append(path)
            # else:
            #     # add file node from path
            #     source_path = source_fs.getsyspath(path)
            #     file_data = {
            #         "source_path": source_path,
            #         "size": info.size,
            #         "hash": file_sha256(source_path)
            #     }

            #     root_node.add_file_node(path, **file_data)
        

    return paths_list

def filter(paths_list, exclude_arguments=None):
    """ Filter paths_list by exclude_arguments.

    Args:
        paths_list (list)
        exclude_arguments (string)

    Returns:
        list
    """

    if not exclude_arguments:
        # return copy of list if no arguments for exclusion
        return list(paths_list)

    filtered_paths_list = []
    
    for path in paths_list:
        # split exclude arguments into parts
        exclude_parts = exclude_arguments.split(",")

        matches = []

        for exclude_part in exclude_parts:
            replace_dict = {
                "*": r".*",
                ".": r"\.",
                "/": r"\/"
            }
            prepared_pattern = replace(exclude_part, replace_dict)

            re_pattern = re.compile(prepared_pattern, re.DOTALL)

            if re.match(re_pattern, path):
                matches.append(True)

        if True in matches:
            # if there are any matches at all, skip
            continue

        # if there are no matches, append path to filtered_paths_list
        filtered_paths_list.append(path)

    return filtered_paths_list 