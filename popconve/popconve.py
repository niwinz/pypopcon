#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import argparse
import json
import io
import os
import uuid
import sys

from os import path

import requests
import pip

DEFAULT_POPCON_URL = "http://localhost:8000/publish/"


def _get_virtualenv_uuid():
    virtual_env_path = os.getenv('VIRTUAL_ENV', '')

    if not virtual_env_path:
        raise RuntimeError('VirtualEnv Needed')

    uuid_file_path = path.join(virtual_env_path, 'popcon.uuid')
    if path.isfile(uuid_file_path):
        with io.open(uuid_file_path, "rt") as f:
            return f.read().strip()

    new_uuid = uuid.uuid1().hex
    with io.open(uuid_file_path, "wt") as f:
        f.write(new_uuid)

    return new_uuid


def _build_installation_data():
    return {"apps": [{"name": app.name, "version": app.version}
                     for app in pip.get_installed_distributions()]}


def _publish(options):
    url = options.url

    if url.endswith("/"):
        url = url[:-1]

    publish_url = "{url}/{uuid}".format(url=url, uuid=_get_virtualenv_uuid())
    publish_data = _build_installation_data()

    response = requests.put(publish_url, data=json.dumps(publish_data))
    if response.status_code in (200, 201):
        print("Publish successful", file=sys.stderr)
        return 0

    print("Error on publish", file=sys.stderr)
    return 1


def _main():
    parser = argparse.ArgumentParser(
        description='Popcon command line interface')
    parser.add_argument("--version", dest="version", action="store_true",
                        default=False, help="Show version.")
    parser.add_argument("--url", dest="url", default=DEFAULT_POPCON_URL,
                        action="store", help="Override default url of service")

    subparsers = parser.add_subparsers(help='sub commands')
    publish_parser = subparsers.add_parser("publish",
                                           help="Publish your package list")
    publish_parser.set_defaults(which="publish")

    if len(sys.argv[1:]) == 0:
        parser.print_help()
        return 0

    options = parser.parse_args()
    if options.which == "publish":
        return _publish(options)

    return 1


if __name__ == "__main__":
    sys.exit(_main())
