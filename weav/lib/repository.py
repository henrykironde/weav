"""Checks the repository for updates."""
from __future__ import print_function

from future import standard_library

standard_library.install_aliases()
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import imp
from pkg_resources import parse_version
from weav.lib.defaults import REPOSITORY, SCRIPT_WRITE_PATH, HOME_DIR
from weav.lib.models import file_exists


def _download_from_repository(filepath, newpath, repo=REPOSITORY):
    """Download latest version of a file from the repository."""
    try:
        urllib.request.urlretrieve(repo + filepath, newpath)
    except:
        raise


def check_for_updates(quite=True):
    """Check for updates to scripts.

    This updates the HOME_DIR scripts directory with the latest script versions
    """
    try:
        # open version.txt for current release branch and get script versions
        version_file = urllib.request.urlopen(REPOSITORY + "version.txt")
        version_file.readline()

        # read scripts from the repository and the checksums from the version.txt
        scripts = []
        for line in version_file:
            scripts.append(line.decode().strip('\n').split(','))

        total_script_count = len(scripts)

        # create script directory if not available
        if not os.path.isdir(SCRIPT_WRITE_PATH):
            os.makedirs(SCRIPT_WRITE_PATH)

        if not quite:
            print("Downloading scripts...")
            _update_progressbar(0.0 / float(total_script_count))
        for index, script in enumerate(scripts):
            script_name = script[0]
            if len(script) > 1:
                script_version = script[1]
            else:
                script_version = None

            path_script_name = os.path.normpath(os.path.join(HOME_DIR, "scripts", script_name))
            if not file_exists(path_script_name):
                _download_from_repository("scripts/" + script_name,
                                          os.path.normpath(os.path.join(SCRIPT_WRITE_PATH, script_name)))

            need_to_download = False
            try:
                file_object, pathname, desc = imp.find_module(''.join(script_name.split('.')[:-1]), [SCRIPT_WRITE_PATH])
                new_module = imp.load_module(script_name, file_object, pathname, desc)
                m = str(new_module.SCRIPT.version)
                need_to_download = parse_version(str(script_version)) > parse_version(m)
            except:
                pass
            if need_to_download:
                try:
                    os.remove(os.path.normpath(os.path.join(HOME_DIR, "scripts", script_name)))
                    _download_from_repository("scripts/" + script_name,
                                              os.path.normpath(os.path.join(SCRIPT_WRITE_PATH, script_name)))
                except Exception as e:
                    print(e)
                    pass
            if not quite:
                _update_progressbar(float(index + 1) / float(total_script_count))
    except:
        raise
    if not quite:
        print("\nThe weav is up-to-date")


def _update_progressbar(progress):
    """Show progressbar.

    Takes a number between 0 and 1 to indicate progress from 0 to 100%.
    And set the bar_length according to the console size
    """
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
        bar_length = int(columns) - 35
        if not bar_length > 1:
            bar_length = 20
    except:
        # Default value if determination of console size fails
        bar_length = 20
    block = int(round(bar_length * progress))
    text = "\rDownload Progress: [{0}] {1:.2f}%".format(
        "#" * block + "-" * (bar_length - block), progress * 100)
    sys.stdout.write(text)
    sys.stdout.flush()
