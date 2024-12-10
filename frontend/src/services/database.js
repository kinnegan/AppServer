import { MongoClient } from "mongodb";

const uri = "mongodb://192.168.1.5:27017";
const dbName = "co2";

const client = new MongoClient(uri);

export const connectToDatabase = async () => {
  try {
    if (!client.isConnected()) {
      await client.connect();
    }
    return client.db(dbName);
  } catch (error) {
    console.error("Failed to connect to the database:", error);
    throw error;
  }
};

export const fetchDevices = async () => {
  try {
    const db = await connectToDatabase();
    const devices = await db.collection("DeviceInfo").find().toArray();
    return devices;
  } catch (error) {
    console.error("Failed to fetch devices:", error);
    return [];
  }
};

export const fetchMeasurements = async (externalId) => {
  try {
    const db = await connectToDatabase();
    const measurements = await db
      .collection("Measurements")
      .find({ external_id: externalId })
      .toArray();
    return measurements;
  } catch (error) {
    console.error("Failed to fetch measurements:", error);
    return [];
  }
};
