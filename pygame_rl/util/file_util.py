# Native modules
import os

# Third-party modules
import pkg_resources
import yaml

# Package name
PACKAGE_NAME = 'pygame_rl'


def get_resource_path(resource_name):
    """Get the resource path.

    Args:
        resource_name (str): The resource name relative to the project root
            directory.

    Returns:
        str: The true resource path on the system.
    """
    package = pkg_resources.Requirement.parse(PACKAGE_NAME)
    return pkg_resources.resource_filename(package, resource_name)


def read_yaml(filename):
    """Read a yaml file.

    Args:
        filename (str): The yaml filename.

    Returns:
        dict: The yaml config.
    """
    with open(filename, 'r') as stream:
        obj = yaml.safe_load(stream)
    stream.close()
    return obj


def resolve_path(path1, path2):
    """Resolve the path.

    Args:
        path1 (str): The base path.
        path2 (str): The relative path to path1.

    Returns:
        str: The resolved path.
    """
    # Get the directory at which the file is
    path1_dir = os.path.dirname(path1)
    # Join the paths of the file directory and the map path
    joined_path = os.path.join(path1_dir, path2)
    # Normalize the path
    return os.path.normpath(joined_path)
