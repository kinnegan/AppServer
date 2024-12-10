import React, { createContext, useState } from "react";

export const DataContext = createContext();

export const DataProvider = ({ children }) => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [measurements, setMeasurements] = useState([]);

  return (
    <DataContext.Provider
      value={{
        devices,
        setDevices,
        selectedDevice,
        setSelectedDevice,
        measurements,
        setMeasurements
      }}
    >
      {children}
    </DataContext.Provider>
  );
};
