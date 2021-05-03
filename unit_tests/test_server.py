import sys
sys.path.append('dropbox')
import os, shutil
from os.path import join, isdir
from server import CustomHandler
from http.server import HTTPServer
import requests
from threading import Thread
import filecmp
import json


TEST_SRC = join('unit_tests', 'test_source')
TEST_FILENAME='first.txt'

TEST_DST = join('unit_tests', 'test_destination')
# Can't upload empty folders to gihub
if not isdir(TEST_DST):
    os.mkdir(TEST_DST)
SERVER_PORT = 8080
SERVER_URL = f'http://127.0.0.1:{SERVER_PORT}'


class TestCustomHandler():
    ''' Doesn't really adhere to the definition of a unit test, but is useful '''

    def run_server_while_true(self):
        with HTTPServer(("", SERVER_PORT), CustomHandler) as self.server:
            self.server.destination_dir = TEST_DST
            self.server.allow_reuse_address = False
            while self.keep_running:
                self.server.handle_request()
    
    def setUp(self):
        # Clear out TEST_DST
        for filename in os.listdir(TEST_DST):
            file_path = os.path.join(TEST_DST, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # TODO: There's got to be a better way than messing with threads.
        # Probably use asyncio next time
        self.keep_running = True
        self.server_thread = Thread(target=self.run_server_while_true, args=[])
        self.server_thread.start()

    def test_upload(self):
        src_file_path = join(TEST_SRC, TEST_FILENAME)
        with open(src_file_path) as src_file:
            r = requests.post(
                f'{SERVER_URL}/upload',
                files={'file': src_file}
            )
        assert r.status_code == 200
        assert filecmp.cmp(
            src_file_path, join(TEST_DST, TEST_FILENAME), shallow=False)
    
    def test_get(self):
        r = requests.get(SERVER_URL)
        assert r.status_code == 200
        assert json.loads(r.content) == {        
            filename: os.stat(join(TEST_DST, filename)).st_mtime
            for filename in os.listdir(TEST_DST)
        }

    def test_delete(self):
        r = requests.post(
            f'{SERVER_URL}/delete',
            data=json.dumps([TEST_FILENAME, 'mock.txt'])
        )
        assert r.status_code == 200
        assert os.listdir(TEST_DST) == []

    def test_duplicate(self):
        r = requests.post(
            f'{SERVER_URL}/duplicate',
            data=json.dumps([TEST_FILENAME, 'mock.txt'])
        )
        assert r.status_code == 200
        assert os.listdir(TEST_DST) == [TEST_FILENAME, 'mock.txt']

    def tearDown(self):
        print('Tearing down server')
        self.keep_running = False
        # TODO: A bit messy: send an empty post request to check self.keep_running again
        r = requests.post(SERVER_URL)
        self.server_thread.join()

if __name__ == '__main__':
    test_class = TestCustomHandler()
    test_class.setUp()
    try:
        test_class.test_upload()
        test_class.test_duplicate()
        test_class.test_get()
        test_class.test_delete()
    except Exception:
        test_class.tearDown()
        raise
    else:
        test_class.tearDown()
        print('Test passed!')
