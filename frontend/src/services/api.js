const API_URL = "http://192.168.1.5:8000/api";

export const fetchDevices = async () => {
  const response = await fetch(`${API_URL}/devices`);
  return response.json();
};

export const fetchMeasurements = async (deviceId) => {
  const response = await fetch(`${API_URL}/measurements/${deviceId}`);
  return response.json();
};
