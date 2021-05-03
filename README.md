# Dropbox Exercise

## Getting Started
This has been developed on Windows for Python 3.9.4, and has not been tested on other platforms.

Spin up the server first using the following command:
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

I've spent an afternoon, and a seperate evening on this, not sure about number of hours - maybe 8.