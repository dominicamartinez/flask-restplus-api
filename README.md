# API Using Flask

This work was done in order to satisfy the requirements of a take home. 

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

## Considerations

- Assumptions

  - The requirements file says "Assume that rates in this file will never overlap" which I'm taking to mean that no time intervals per rate detail will overlap for each day and hour.

  - The requirements file says "Assume that there could be other (non America/Chicago) timezones specified." I didn't know whether this meant 1 specific timezone per rates file or multiple timezones within the same rates file. I assumed the latter and, thus, supported multiple timezones per file. However, keeping in mind, the above assumption, there is no error-checking for 2 different rates across 2 different timezones which may overlap.

- Logging

Aside from trivial metrics or information, there should exist logging if this was to continue on to be a full-fledged application in a production environment.

- Security

Since this is a take home assessment there is clearly a severe lack of security for this type of set up. There are many ways to protect an API which exist outside the scope of this work. 

- Data Persistence 

Storing information like the rates inside of Flask's config variables to be persisted across different API calls is certainly not the best place, however, it does work for small scale applications like this.

## Notes

- The format of the rates JSON file is probably not the best representation of the data,
validation and parsing might be easier without a different layout

- There could be a number of optimizations on some of the processing and data structures. Example would be parseData method, whereby there exists 3 passes of the data to build out the internal data structure for the rates information. 

- The metrics within the info endpoint can be used for something like a load balancer health check combined with other metrics, aside from the simple statistics on the price endpoint that I implemented, that weren't explored.