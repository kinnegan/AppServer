import React, { useEffect, useContext, useState } from "react";
import DeviceSelector from "../components/DeviceSelector";
import Graph from "../components/Graph";
import Stats from "../components/Stats";
import { fetchDevices, fetchMeasurements } from "../services/api";
import { DataContext } from "../context/DataContext";

const Dashboard = () => {
  const {
    devices,
    setDevices,
    selectedDevice,
    setSelectedDevice
  } = useContext(DataContext);

  const [temperatureData, setTemperatureData] = useState([]);
  const [humidityData, setHumidityData] = useState([]);
  const [co2Data, setCo2Data] = useState([]);

  useEffect(() => {
    const loadDevices = async () => {
      const data = await fetchDevices();
      //console.log("Devices fetched:", data);  // Логируем устройства
      setDevices(data);
    };
    loadDevices();
  }, [setDevices]);

  useEffect(() => {
    if (selectedDevice) {
      const loadMeasurements = async () => {
        const data = await fetchMeasurements(selectedDevice);
        //console.log("Measurements fetched:", data);  // Логируем полученные измерения

        // Преобразуем данные в нужный формат
        const temperatureFormatted = formatData(data.temperature, "avg_temperature");
        const humidityFormatted = formatData(data.humidity, "avg_humidity");
        const co2Formatted = formatData(data.co2, "avg_co2");

        //console.log("Formatted Temperature data:", temperatureFormatted);
        //console.log("Formatted Humidity data:", humidityFormatted);
        //console.log("Formatted CO2 data:", co2Formatted);

        setTemperatureData(temperatureFormatted);
        setHumidityData(humidityFormatted);
        setCo2Data(co2Formatted);
      };
      loadMeasurements();
    }
  }, [selectedDevice]);

  // Функция для форматирования данных
  const formatData = (data, valueKey) => {
    //console.log(`Formatting data for ${valueKey}`);  // Логируем, что форматируем
    return data.map(item => ({
      timestamp: item.timestamp,
      value: item[valueKey]
    }));
  };

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
          <Graph
            title="Temperature"
            data={temperatureData}
            color="red"
          />
          <Graph
            title="Humidity"
            data={humidityData}
            color="blue"
          />
          <Graph
            title="CO2"
            data={co2Data}
            color="green"
          />
          <Stats measurements={{ temperature: temperatureData, humidity: humidityData, co2: co2Data }} />
        </>
      )}
    </div>
  );
};

export default Dashboard;
