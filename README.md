# API Using Flask

## Build and Run

This project contains a Dockerfile which will build a Docker image with the following command:
```
docker build -t backend-dm .
```

Command to run Docker container:
```
docker run -d -p 5000:5000 backend-dm
```

## Usage and Test

The Swagger UI is available at the root URL of the deployed container 
```
http://localhost:5000
```
The Swagger Spec can also be found to the top left in a hyperlink for swagger.json

The API is testable via the Swagger UI, there are also a Python unittest file inside of the test folder, which when run with the following command (assuming Python 3.8+):
```
python3 test/testAPI.py -v   ## depending on system, may just be python
```
will output the values of the unit tests.