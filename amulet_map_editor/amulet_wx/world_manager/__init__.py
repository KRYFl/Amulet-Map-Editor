import wx
import os
from typing import List
from amulet_map_editor.amulet_wx.wx_util import SimpleNotebook, SimplePanel
from amulet import world_interface
import importlib
import pkgutil

# this is where most of the magic will happen

_extensions: List['BaseWorldTool'] = []


def load_extensions():
    if not _extensions:
        for _, name, _ in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), 'extensions')]):
            # load module and confirm that all required attributes are defined
            module = importlib.import_module(f'amulet_map_editor.amulet_wx.world_manager.extensions.{name}')

            if hasattr(module, 'export'):
                export = getattr(module, 'export')
                if 'ui' in export and issubclass(export['ui'], BaseWorldTool):
                    _extensions.append([export.get('name', 'missingno'), export['ui']])


class WorldManagerUI(SimpleNotebook):
    def __init__(self, parent, path):
        SimpleNotebook.__init__(
            self,
            parent,
            wx.NB_LEFT
        )
        self._finished = False
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._page_change)
        self.world = world_interface.load_world(path)
        self.world_name = self.world.world_wrapper.world_name
        self._extensions: List[BaseWorldTool] = []
        self._last_extension: int = -1
        self._load_extensions()
        self._finished = True

    def _load_extensions(self):
        load_extensions()
        for extension_name, extension in _extensions:
            ext = extension(self, self.world)
            self._extensions.append(ext)
            self.AddPage(ext, extension_name, True)

    def close_world(self):
        self.GetParent().DeletePage(self.GetParent().FindPage(self))
        self.Destroy()
        for ext in self._extensions:
            ext.close()
        self.world.close()

    def _page_change(self, evt):
        if self._finished:
            self._extensions[self._last_extension].disable()
            self._extensions[self.GetSelection()].enable()
        self._last_extension = self.GetSelection()
        evt.Skip()


class BaseWorldTool(SimplePanel):

    def enable(self):
        """Run when the panel is shown/enabled"""
        pass

    def disable(self):
        """Run when the panel is hidden/disabled"""
        pass

    def close(self):
        """Run when the world is closed"""
        pass