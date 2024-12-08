## **Simple Application Server for Celsium IoT**

This is a simply python backend for catching data from Celsium IoT devices.

## **Introduction**

This is a very simple project, created for personal usage omly and have no frontend jet. They have API key for receiving data flow from Celsium IoT (only for CO2) and keeping it in MongoDB. DB should be created independently. Another two key's could be used for receiving data from DB. All key's described by swagger OpenAPI

## **Installation**

No installation is needed, just run it as docker. Keep in mind that you should have MongoDB and create DB and COLLECTION befor usage:

1. Clone the repository: **`git clone https://github.com/kinnegan/AppServer.git`**
2. Create .env file in a root directory:
```
MONGO_URI=mongodb://mongodb_uri:27017/
MONGO_DB=co2
MONGO_DEVICE_COLLECTION=DeviceInfo
MONGO_DATA_COLLECTION=Measurements
```
3. Run Docker compose from root directory: **`docker compose up --build`**

Or start directly:

1. Navigate to the project directory: **`cd src/modules`**
2. Run: **`gunicorn -k uvicorn.workers.UvicornWorker apis:app --bind 0.0.0.0:8000`**


## **Usage**

To use Application Server, follow these steps:

1. Create configuration on SCEF (or NEF) sever with notificationDestination.
2. Or use something like Postman and send/receive command to API.

## **Example**

1. POST data
    url: **`http://IPADDR:8000/api/test`**
    data fromat:
    ```
    {"externalId": "eample@exteranl.id",
    "niddConfiguration": "/3gpp-nidd/v1/<ScsAsID>/configurations/<configuration ID>",
    "reliableDataService": false,
    "data": "A4QRAgMDFfcRBwhSZ0AJfAb/////0wHsFg=="
    }
    ```
2. GET devices list
    url: **`http://IPADDR:8000/api/devices`**
3. GET aggregated data
    url: **`http://IPADDR:8000/api/measurements/eample@exteranl.id`**

Application Server was created by **[kinnegan](https://github.com/kinnegan)**.

