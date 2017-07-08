# Native modules
import yaml


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
