import React from "react";

const average = (data) => {
  if (!Array.isArray(data) || data.length === 0) return 0;
  return data.reduce((sum, value) => sum + value, 0) / data.length;
};

const Stats = ({ measurements }) => {
  if (!Array.isArray(measurements)) {
    return <div>No measurements available</div>;
  }

  const temperatureAvg = average(measurements.map(m => m.temperature));
  const humidityAvg = average(measurements.map(m => m.humidity));
  const co2Avg = average(measurements.map(m => m.co2));

  return (
    <div className="stats">
      <h2>Average Measurements</h2>
      <p>Temperature: {temperatureAvg.toFixed(2)}°C</p>
      <p>Humidity: {humidityAvg.toFixed(2)}%</p>
      <p>CO2: {co2Avg.toFixed(2)} ppm</p>
    </div>
  );
};

export default Stats;
