# Dropbox Exercise

## Getting Started
Dockerized to avoid the headache of developing on windows. Make sure you have docker installed. To spin up the container run:
```
docker build -t dropbox_exercise C:\Users\pc\OneDrive\Appliations\dropbox_exercise\
docker run -it -v C:\Users\pc\OneDrive\Appliations\dropbox_exercise:/usr/src/app dropbox_exercise
docker build -t dropbox_exercise <location of cloned repo>\dropbox_exercise\
docker run -it -v <location of cloned repo>\dropbox_exercise:/usr/src/app dropbox_exercise 
```

To run the client use the following command:
```
python3 dropbox/client.py <source directory>
```

### Unit Tests
To run the unit tests call `pytest`. To do this for a particular file, run:
```
pytest -k <name of test file>
```