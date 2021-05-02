import sys
sys.path.append('dropbox')
import os, shutil
from server import CustomHandler
from http.server import HTTPServer
import requests
from threading import Thread
import filecmp
import logging
import json


TEST_SRC = 'unit_tests/test_source'
TEST_FILENAME='first.txt'

TEST_DST = 'unit_tests/test_destination'
SERVER_PORT = 8080

LOGGER = logging.getLogger('test_server')


class TestCustomHandler():
    ''' Doesn't really adhere to the definition of a unit test, but is useful '''

    def run_server_while_true(self):
        with HTTPServer(("", SERVER_PORT), CustomHandler) as self.server:
            self.server.destination_dir = TEST_DST
            self.server.allow_reuse_address = False
            while self.keep_running:
                self.server.handle_request()
    
    def setUp(self):
        for filename in os.listdir(TEST_DST):
            file_path = os.path.join(TEST_DST, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


        # TODO: There's got to be a better way than messing with threads
        self.keep_running = True
        self.server_thread = Thread(target=self.run_server_while_true, args=[])
        self.server_thread.start()

    def tearDown(self):
        LOGGER.info('Tearing down server')
        self.keep_running = False
        # TODO: A bit messy: send an empty post request to check self.keep_running again
        r = requests.post(f'http://127.0.0.1:{SERVER_PORT}')
        self.server_thread.join()

    def test_upload(self):
        with open(f'{TEST_SRC}/{TEST_FILENAME}') as src_file:
            r = requests.post(
                f'http://127.0.0.1:{SERVER_PORT}/{TEST_FILENAME}',
                files={'file': src_file}
            )
        assert r.status_code == 200
        # TODO: Got to be careful about line endings here - different decode perhaps?
        assert filecmp.cmp(
            f'{TEST_SRC}/{TEST_FILENAME}', f'{TEST_DST}/{TEST_FILENAME}', shallow=False)
    
    def test_get(self):
        # TODO: do I need this?
        r = requests.get(f'http://127.0.0.1:{SERVER_PORT}')
        assert r.status_code == 200
        assert json.loads(r.content) == os.listdir(TEST_DST)

    def test_delete(self):
        r = requests.post(f'http://127.0.0.1:{SERVER_PORT}/{TEST_FILENAME}')
        assert os.listdir(TEST_DST) == []

if __name__ == '__main__':
    test_class = TestCustomHandler()
    test_class.setUp()
    try:
        test_class.test_upload()
        test_class.test_get()
        test_class.test_delete()
    except Exception:
        test_class.tearDown()
        raise
    else:
        test_class.tearDown()
