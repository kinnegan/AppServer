## **Simple Application Server for Celsium IoT**

A simple Python-based backend for receiving and managing data from Celsium IoT devices.

## **Introduction**

This project is a lightweight solution developed for personal use. It currently does not include a frontend. The server uses an API key to receive CO2 data from Celsium IoT devices and stores it in a MongoDB database. Note that the MongoDB database must be set up independently. 

Additional API keys are available for retrieving data from the database. All keys are documented via Swagger (OpenAPI).

## **Installation**

No formal installation is required; the application can be run directly using Docker. Ensure that MongoDB is set up, and the required database and collections are created before running the application.

1. Clone the repository: **`git clone https://github.com/kinnegan/AppServer.git`**
2. Create .env file in a root directory:
```
MONGO_URI=mongodb://mongodb_uri:27017/
MONGO_DB=co2
MONGO_DEVICE_COLLECTION=DeviceInfo
MONGO_DATA_COLLECTION=Measurements
SERVER_HOST=set_server_ip
SERVER_PORT=set_server_port
```
Default value fro SERVER is **localhost:8000**
Default value for MONGO is **mongodb://localhost:27017/**, **co2** for database, **DeviceInfo** and **Measurements** collections

3. Run Docker compose from root directory: **`docker compose up --build`**

Alternatively, run the application directly without Docker:

1. Navigate to the project directory: **`cd src/modules`**
2. Start the server: **`gunicorn -k uvicorn.workers.UvicornWorker apis:app --bind 0.0.0.0:8000`**


## **Usage**

To interact with the Application Server:

1. Configure the **notificationDestination** on the SCEF (or NEF) server.
2. Alternatively, use tools like Postman to send and receive API commands.

## **Example**

1. POST data
    url: **`http://IPADDR:8000/api/test`**
    **Request Body**:
    ```
    {"externalId": "eample@exteranl.id",
    "niddConfiguration": "/3gpp-nidd/v1/<ScsAsID>/configurations/<configuration ID>",
    "reliableDataService": false,
    "data": "A4QRAgMDFfcRBwhSZ0AJfAb/////0wHsFg=="
    }
    ```
2. GET Device List
    url: **`http://IPADDR:8000/api/devices`**
3. GET Aggregated Data
    url: **`http://IPADDR:8000/api/measurements/eample@exteranl.id`**

Application Server was created by **[kinnegan](https://github.com/kinnegan)**.

