import os
import sys
import yaml

from ._base import BaseFinder, BaseLoader, InvalidYamlError


class YamlFinder(BaseFinder):

    def __init__(self, *args, **kwargs):
        super(YamlFinder, self).__init__(*args, **kwargs)

    def find_module(self, fullname, path=None):

        if '.' in fullname:
            fullname = os.path.join(*([self.dir] + fullname.split('.')))

        if os.path.isfile(fullname + '.yaml'):
            return YamlLoader(self.dir)
        elif os.path.isfile(fullname + '.yml'):
            return YamlLoader(self.dir, extension='yml')
        else:
            return None


class YamlLoader(BaseLoader):

    TYPE = 'yaml'

    def __init__(self, dir, extension=None):
        self.e = None
        self.err_msg = None
        self.TYPE = extension if extension else self.TYPE
        super(YamlLoader, self).__init__(dir)

    def load_module(self, fullname):
        """
        load_module is always called with the same argument as finder's
        find_module, see "How Import Works"
        """
        mod = super(YamlLoader, self).load_module(fullname)

        if '.' in fullname:
            fullname = os.path.join(*([self.dir] + fullname.split('.')))

        fullname = fullname + '.' + self.TYPE

        with open(fullname) as f:
            try:
                for doc in yaml.load_all(f, yaml.Loader):
                    if isinstance(doc, dict):
                        mod.__dict__.update(doc)
            except yaml.YAMLError:
                self.e = "YAMLError"
                self.err_msg = sys.exc_info()[1]

        if self.e == "YAMLError":
            err_msg = '\n' + self.TYPE + " not valid: "
            err_msg += fullname + '\n'
            err_msg += str(self.err_msg)
            raise InvalidYamlError(err_msg)

        return mod
