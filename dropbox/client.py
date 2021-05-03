''' 
A simple command line client which keeps monitoring changes in a given directory, and
uploads any change to it's server
'''
import os
import time
from os.path import isdir, join
from argparse import ArgumentParser
import requests
import json
import logging
import filecmp


SERVER_PORT = 8000
SERVER_URL = f'http://127.0.0.1:{SERVER_PORT}'
LOGGER = logging.getLogger('client')


parser = ArgumentParser(
    description=__doc__
)
# Don't use the dash prefix to make an arg positional
parser.add_argument('src_dir', help='The source directory for which to monitor file changes')


class SourceMonitor():

    def __init__(self, src_dir, check_interval=5):
        # Sanity check
        assert isdir(src_dir), 'The supplied argument is not a directory'
        self.src_dir = src_dir
        self.sync_dst_with_src = True
        # How often to check the src directory
        self.check_interval = check_interval

    def watch_directory(self):
        '''
            Watch the source directory and upload files to/delete files from the destination
            directory
        '''
        dst_files = {}
        while self.sync_dst_with_src:
            time.sleep(self.check_interval)

            src_files = {
                filename: os.stat(join(self.src_dir, filename)).st_mtime
                for filename in os.listdir(self.src_dir)
            }
            added = [filename for filename in src_files.keys() if filename not in dst_files]
            modified = [
                filename for filename in set(src_files.keys()).intersection(set(dst_files.keys()))
                if src_files[filename] > dst_files[filename]
            ]

            # Can only check the contents of files client side
            # TODO: probably not very efficient to use sets here
            remaining = set(src_files.keys()).intersection(set(dst_files))
            for filename in added + modified:
                duplicate_name = None
                potential_copies = remaining.difference({filename})
                for potential_copy in potential_copies:
                    if filecmp.cmp(
                        join(self.src_dir, filename), join(self.src_dir, potential_copy),
                        shallow=False
                    ):
                        duplicate_name = potential_copy
                        break
                if duplicate_name:
                    LOGGER.info(
                        f'Informing the server that {filename} has the same content as'
                        f'{duplicate_name} (which exists server-side)'
                    )
                    r = requests.post(
                        f'{SERVER_URL}/duplicate',
                        data=json.dumps([duplicate_name, filename])
                    )
                else:
                    LOGGER.info(f'Uploading {filename} to the destination')
                    with open(join(self.src_dir, filename)) as src_file:
                        r = requests.post(
                            f'{SERVER_URL}/upload',
                            files={'file': src_file}
                        )
                    # If we have uploaded a file, we can now duplicate & rename it
                    remaining.add(filename)
            removed = [filename for filename in dst_files.keys() if filename not in src_files]
            if removed:
                LOGGER.info(f'Deleting {removed} from the destination')
                r = requests.post(
                    f'{SERVER_URL}/delete',
                    data=json.dumps(removed)
                )
            r = requests.get(SERVER_URL)
            assert r.status_code == 200
            dst_files = json.loads(r.content)
        LOGGER.info('Client stopped')


if __name__ == '__main__':
    args = parser.parse_args()
    SourceMonitor(args.src_dir).watch_directory()
