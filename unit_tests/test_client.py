import sys
sys.path.append('dropbox')
from client import SourceMonitor


TEST_SRC = 'unit_tests/test_source'


class TestSourceMonitor():
    ''' Unit tests for SourceMonitor '''

    def test__init__(self):
        ''' Check __init__ '''
        assert SourceMonitor(TEST_SRC).src_dir == TEST_SRC

if __name__ == '__main__':
    TestSourceMonitor().test__init__()
    # TODO: write a unit test for SourceMonitor.
    # I didn't want to spend time doing this because:
    # - I was already close to going outside the scope of a 'coding test'. Unit testing the client
    # is non-trivial as I'd probably want to use the python unit test framework and mock out 
    # requests.
    # - the client is implicitly tested to some degree in the integration test.
