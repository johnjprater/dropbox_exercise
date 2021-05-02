import sys
sys.path.append('dropbox')
from client import SourceMonitor


TEST_SOURCE = 'unit_tests/test_source/'


class TestSourceMonitor():
    ''' Unit tests for SourceMonitor '''

    def test__init__(self):
        ''' Check __init__ '''
        # Relative path from where pytest and the app is run.
        assert SourceMonitor(TEST_SOURCE).source_dir == TEST_SOURCE
        # Should also accept an absolute path
        assert SourceMonitor('/home').source_dir == '/home'

