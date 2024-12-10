import React, { useEffect, useContext } from "react";
import DeviceSelector from "../components/DeviceSelector";
import Graph from "../components/Graph";
import Stats from "../components/Stats";
import { fetchDevices, fetchMeasurements } from "../services/database";
import { DataContext } from "../context/DataContext";

const Dashboard = () => {
  const {
    devices,
    setDevices,
    selectedDevice,
    setSelectedDevice,
    measurements,
    setMeasurements,
  } = useContext(DataContext);

  useEffect(() => {
    const loadDevices = async () => {
      const data = await fetchDevices();
      setDevices(data);
    };
    loadDevices();
  }, [setDevices]);

  useEffect(() => {
    if (selectedDevice) {
      const loadMeasurements = async () => {
        const data = await fetchMeasurements(selectedDevice);
        setMeasurements(data);
      };
    loadMeasurements();
    }
  }, [selectedDevice, setMeasurements]);

  return (
    <div className="dashboard">
      <h1>Device Dashboard</h1>
      <DeviceSelector
        devices={devices}
        selectedDevice={selectedDevice}
        onSelect={setSelectedDevice}
      />
      {selectedDevice && (
        <>
          <Graph measurements={measurements} />
          <Stats measurements={measurements} />
        </>
      )}
    </div>
  );
};

export default Dashboard;
