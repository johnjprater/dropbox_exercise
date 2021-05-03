import os, shutil
from os.path import join, isdir
from dropbox.server import CustomHandler
from dropbox.client import SourceMonitor, SERVER_PORT, SERVER_URL
from http.server import HTTPServer
import requests
from threading import Thread
import filecmp
import time


TEST_SRC = join('unit_tests', 'test_source')
TEST_FILENAME='first.txt'

TEST_DST = join('unit_tests', 'test_destination')
# Can't upload empty folders to gihub
if not isdir(TEST_DST):
    os.mkdir(TEST_DST)

# Make this quicker for a test
TEST_CHECK_INTERVAL = 2


class IntegrationTest():
    ''' Doesn't really adhere to the definition of a unit test, but is useful '''

    def run_server_while_true(self):
        with HTTPServer(("", SERVER_PORT), CustomHandler) as self.server:
            self.server.destination_dir = TEST_DST
            self.server.allow_reuse_address = False
            while self.keep_running:
                self.server.handle_request()
    
    def run_client(self):
        self.client = SourceMonitor(TEST_SRC, check_interval=TEST_CHECK_INTERVAL)
        self.client.watch_directory()
    
    def setUp(self):
        for filename in os.listdir(TEST_DST):
            file_path = os.path.join(TEST_DST, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        self.keep_running = True
        self.server_thread = Thread(target=self.run_server_while_true, args=[])
        self.server_thread.start()
        # Wait for client to stop
        time.sleep(TEST_CHECK_INTERVAL)
        self.client = None
        self.client_thread = Thread(target=self.run_client, args=[])
        self.client_thread.start()

    def runTest(self):
        print('Checking that the client deletes multiple unwanted files')
        for i in range(4):
            shutil.copy(join(TEST_SRC, 'first.txt'), join(TEST_DST, f'cruft_{i}.txt'))
        self.check_src_and_dst_are_in_sync()

        print('Checking multiple uploads')
        for i in range(4):
            shutil.copy(join(TEST_SRC, 'first.txt'), join(TEST_SRC, f'{i}.txt'))
        self.check_src_and_dst_are_in_sync()

        print('Checking multiple deletes')
        for i in range(4):
            os.remove(join(TEST_SRC, f'{i}.txt'))
        self.check_src_and_dst_are_in_sync()

        print('Check renaming a file')
        os.rename(join(TEST_SRC, 'first.txt'), join(TEST_SRC, 'second.txt'))
        self.check_src_and_dst_are_in_sync()
        shutil.copyfile(join(TEST_SRC, 'second.txt'), join(TEST_SRC, 'first.txt'))
        self.check_src_and_dst_are_in_sync()

        print('Check modifying a file')
        with open(join(TEST_SRC, 'second.txt'), 'a') as f:
            f.write('Hello World!')
        self.check_src_and_dst_are_in_sync()
        os.remove(join(TEST_SRC, 'second.txt'))
        self.check_src_and_dst_are_in_sync()

    def check_src_and_dst_are_in_sync(self):
        # Try to avoid race conditions by checking that the src and dst are in sync *eventually*
        # TODO: improve this
        time.sleep(3 * TEST_CHECK_INTERVAL)
        for src_file, dst_file in zip(os.listdir(TEST_SRC), os.listdir(TEST_DST)):
            src_file_path = join(TEST_SRC, src_file)
            dst_file_path = join(TEST_DST, dst_file)
            assert filecmp.cmp(src_file_path, dst_file_path, shallow=False)
    
    def tearDown(self):
        # time.sleep(2)
        print('Stopping client')
        self.client.sync_dst_with_src = False
        self.client_thread.join()
        time.sleep(TEST_CHECK_INTERVAL)
        # print('Tearing down server')
        self.keep_running = False
        r = requests.post(SERVER_URL)
        self.server_thread.join()

if __name__ == '__main__':
    test_class = IntegrationTest()
    test_class.setUp()
    try:
        test_class.runTest()
    except Exception:
        test_class.tearDown()
        raise
    else:
        test_class.tearDown()
        print('Test passed!')