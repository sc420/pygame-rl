# Native modules
import os

# Testing targets
import pygame_soccer.util.file_util as file_util


class FileUtilTest:
  def test_get_resource_path(self):
    resource_name = 'pygame_soccer/data/map/soccer.tmx'
    resource_path = file_util.get_resource_path(resource_name)
    assert os.path.normpath(resource_name) in resource_path

  def test_read_yaml(self):
    resource_name = 'pygame_soccer/data/map/agent_sprite.yaml'
    resource_path = file_util.get_resource_path(resource_name)
    contents = file_util.read_yaml(resource_path)
    assert len(contents) > 0

  def test_resolve_path(self):
    path1 = 'dir1/file1'
    path2 = 'dir2/file2'
    expected_path = 'dir1/dir2/file2'
    resolved_path = file_util.resolve_path(path1, path2)
    assert os.path.normpath(expected_path) == resolved_path
