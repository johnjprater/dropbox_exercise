''' TODO '''
import os
import time
from os.path import isdir
from argparse import ArgumentParser
import requests


parser = ArgumentParser(
    description= (
        'A simple command line client which keeps monitoring changes in a given directory, and'
        ' uploads any change to it\'s server'
    )
)
# Don't use the dash prefix to make an arg positional
parser.add_argument('source_dir', help='The source directory for which to monitor file changes')


class SourceMonitor():
    ''' TODO '''

    def __init__(self, source_dir):
        ''' TODO '''
        # Sanity check
        assert isdir(source_dir), 'The supplied argument is not a directory'
        self.source_dir = source_dir

    def watch_directory(self):
        # before = {
        #     filename: os.stat(self.source_dir + filename).st_mtime
        #     for filename in os.listdir(self.source_dir)
        # }
        before = {}
        while True:
            time.sleep(5)
            after = {
                filename: os.stat(self.source_dir + filename).st_mtime
                for filename in os.listdir(self.source_dir)
            }
            added = [filename for filename in after.keys() if filename not in before]
            modified = [
                filename for filename in set(after.keys()).intersection(set(before.keys()))
                if after[filename] > before[filename]
            ]
            for filename in added + modified:
                # POST with a file should upload
                with open(f'{ self.source_dir}/{filename}') as src_file:
                    r = requests.post(
                        f'http://127.0.0.1:8000/{filename}',
                        files={'file': src_file}
                    )
            removed = [filename for filename in before.keys() if filename not in after]
            for filename in removed:
                # Empty POST should delete a file
                r = requests.post(f'http://127.0.0.1:8000/{filename}')

            before = after


if __name__ == '__main__':
    args = parser.parse_args()
    SourceMonitor(args.source_dir).watch_directory()