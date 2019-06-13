#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python client for Hiera hierachical database."""

from __future__ import print_function, unicode_literals

import json
import logging
import os.path
import subprocess

import hiera.exc

__all__ = ('HieraClient',)


class HieraClient(object):
    __doc__ = __doc__

    def __init__(self, config_filename, hiera_binary='hiera', **kwargs):
        """Create a new instance with the given settings.

        Key value params passed into this will be added to the environment when
        running the hiera client. For example, (environment='developer',
        osfamily='Debian') as keyword args to __init__ would result in hiera
        calls like this:

          hiera --config <config_filename> <key> environment=developer \
            osfamily=Debian

        :param config_filename: Path to the hiera configuration file.
        :param hiera_binary: Path to the hiera binary. Defaults to 'hiera'.
        """
        self.config_filename = config_filename
        self.hiera_binary = hiera_binary
        self.environment = kwargs

        self._validate()
        logging.debug('New Hiera instance: {0}'.format(self))

    def __repr__(self):
        """String representations of Hiera instance."""
        def kv_str(key):
            """Takes an instance attribute and returns a string like:
            'key=value'
            """
            return '='.join((key, repr(getattr(self, key, None))))

        params_list = map(kv_str,
                          ['config_filename', 'hiera_binary', 'environment'])
        params_string = ', '.join(params_list)
        return '{0}({1})'.format(self.__class__.__name__, params_string)

    def get(self, key_name):
        """Request the given key from hiera.

        Returns the string version of the key when successful.

        Raises :class:`hiera.exc.HieraError` if the key does not exist or there
        was an error invoking hiera. Raises
        :class:`hiera.exc.HieraNotFoundError` if the hiera CLI binary could not
        be found.

        :param key_name: string key
        :rtype: str value for key or None
        """
        return self._hiera(key_name)

    def _command(self, key_name):
        """Returns a hiera command list that is suitable for passing to
        subprocess calls.

        :param key_name:
        :rtype: list that is hiera command
        """
        cmd = [self.hiera_binary,
               '--config', self.config_filename,
               '--format', 'json',
               key_name]
        cmd.extend(map(lambda *env_var: '='.join(*env_var),
                       self.environment.iteritems()))
        return cmd

    def _hiera(self, key_name):
        """Invokes hiera in a subprocess with the instance environment to query
        for the given key.

        Returns the string version of the key when successful.

        Raises HieraError if the key does not exist or there was an error
        invoking hiera. Raises HieraNotFoundError if the hiera CLI binary could
        not be found.

        :param key_name: string key
        :rtype: str value for key or None
        """
        hiera_command = self._command(key_name)
        output = None
        try:
            output = subprocess.check_output(
                hiera_command, stderr=subprocess.STDOUT)
        except OSError as ex:
            raise hiera.exc.HieraNotFoundError(
                'Could not find hiera binary at: {0}'.format(
                    self.hiera_binary))
        except subprocess.CalledProcessError as ex:
            raise hiera.exc.HieraError(
                'Failed to retrieve key {0}. exit code: {1} '
                'message: {2} console output: {3}'.format(
                    key_name, ex.returncode, ex.message, ex.output))
        else:
            try:
                value = json.loads(output.strip())
            except ValueError as ex:
                raise hiera.exc.HieraError(
                    'Failed to convert hiera output {0} for key {1}. '
                    'message: {2}'.format(
                        output.strip(), key_name, ex.message))
            if not value:
                return None
            else:
                return value

    def _validate(self):
        """Validate the instance attributes. Raises HieraError if issues are
        found.
        """
        if not os.path.isfile(self.config_filename):
            raise hiera.exc.HieraError(
                'Hiera configuration file does not exist '
                'at: {0}'.format(self.config_filename))
