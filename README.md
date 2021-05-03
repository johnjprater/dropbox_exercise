# Dropbox Exercise

## Getting Started
This has been developed on Windows for Python 3.9.4, and has not been tested on other platforms.

Spin up the server first using the following command (from <location of cloned repo>/dropbox_exercise):
```
python dropbox/server.py <destination directory>
```

Then run the client using the following command:
```
python dropbox/client.py <source directory>
```


### Unit Tests
To run the unit tests call:
```
python .\unit_tests\test_server.py
python .\unit_tests\test_client.py

```

There is also an integration test of some sort, which can be run with:
```
python .\integration_test.py
```

### Comments & Improvements
I've spent an afternoon, and a seperate evening on this, not sure about number of hours - maybe 8.
There are a bunch of TODO's sprinkled around in the code, with small ideas for improvements.

In addition:
- I didn't get onto Bonus 2.
- I would replace HTTPServer and BaseHTTPRequestHandler with a more fleshed out framework e.g. flask.
- I would write unit tests for the client.
- I would have a think about unit tests for the server (the current is more like a module test).
- Think about making this cross-platform (dockerise?).
- Spend some time considering the efficiency of my code (I've only looked at optimizing for data transfer).
- Think more carefully about how the client and server talk to each other.
