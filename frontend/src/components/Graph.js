import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

// Регистрация необходимых компонентов для chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Graph = ({ title, data, color }) => {
  const [chartData, setChartData] = useState({});

  useEffect(() => {
    if (data && data.length > 0) {
      //console.log(`Graph Data Received for ${title}:`, data);

      // Преобразуем timestamp в более читаемый формат и выводим в консоль
      const timestamps = data.map((item) => {
        const timestamp = item.timestamp.replace("Z", ""); // Убираем Z в конце
        const formattedTime = new Date(timestamp); // Преобразуем в объект Date
        //console.log(`Original timestamp: ${item.timestamp}`);
        //console.log(`Formatted with toLocaleString: ${formattedTime.toLocaleString()}`);
        //console.log(`Formatted with toLocaleTimeString: ${formattedTime.toLocaleTimeString()}`);
        
        return formattedTime.toLocaleString(); // Используем toLocaleString для локализованного формата времени
      });

      const values = data.map((item) => item.value);

      const formattedData = {
        labels: timestamps,
        datasets: [
          {
            label: title,
            data: values,
            borderColor: color,
            fill: false
          }
        ]
      };
      setChartData(formattedData);
    } else {
      //console.log("No data available for the chart.");
    }
  }, [data, title, color]);

  return (
    <div className="graph">
      <h3>{title}</h3>
      {chartData.labels ? <Line data={chartData} /> : <p>No data available</p>}
    </div>
  );
};

export default Graph;
