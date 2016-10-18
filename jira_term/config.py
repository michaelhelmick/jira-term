import json
from os import makedirs
from os.path import expanduser, join

import click


class Config(dict):
    def __init__(self, *args, **kwargs):
        self.config = join(expanduser('~'), '.jira')

        try:
            makedirs(self.config)
        except OSError:
            pass

        self.config = join(self.config, 'config.json')

        super(Config, self).__init__(*args, **kwargs)

    def load(self):
        """load a JSON config file from disk"""
        try:
            _config_file = open(self.config, 'r+')
            data = json.loads(_config_file.read())
        except (ValueError, IOError):
            data = {}

        self.update(data)

    def save(self):
    	# self.config.ensure()
        _file = open(self.config, 'w+')
        _file.write(json.dumps(self))

    def _setup(self):
        username = self.get('username')
        password = self.get('password')
        domain = self.get('domain')

        if not username or not password or not domain:
            if not domain:
                domain = click.prompt('Please enter your JIRA domain')

            if not username:
                username = click.prompt('Please enter your JIRA username')

            if not password:
                password = click.prompt('Please enter your JIRA password')

            self['domain'] = domain.rstrip('/')
            self['username'] = username
            self['password'] = password
            self.save()

pass_config = click.make_pass_decorator(Config, ensure=True)
