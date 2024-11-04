import React from "react";
import { Bar } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const transformData = (gamePrediction) => {
  // extract descriptions and importances from top_features_descriptions
  const originalLabels = Object.keys(gamePrediction.top_features_descriptions);
  const importances = Object.values(
    gamePrediction.top_features_descriptions
  ).map(
    (feature) => feature[1] // importance score
  );

  // use numeric labels for the chart
  const legendLabels = originalLabels.map((_, index) => (index + 1).toString());

  return { legendLabels, originalLabels, importances };
};

const BarChart = ({ gamePrediction }) => {
  const { legendLabels, originalLabels, importances } =
    transformData(gamePrediction);

  const chartData = {
    labels: legendLabels,
    datasets: [
      {
        label: "Importance",
        data: importances,
        color: "rgba(255, 255, 255, 1)",
        backgroundColor: "rgba(238, 152, 58, 0.6)",
        borderColor: "rgba(238, 152, 58, 1)",
        borderWidth: 1,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        ticks: {
          color: "#FFFFFF",
        },
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: "#FFFFFF",
        },
        title: {
          display: true,
          text: "Importance",
          color: "#FFFFFF",
        },
      },
    },
    plugins: {
      legend: {
        display: false,
        labels: {
          color: "#FFFFFF",
        },
      },
      tooltip: {
        bodyColor: "#FFFFFF",
        titleColor: "#FFFFFF",
      },
    },
  };

  return (
    <div className="chart-container">
      <Bar data={chartData} options={options} />
      <div className="legend">
        <h4>Reasons:</h4>
        {originalLabels.map((label, index) => (
          <div key={index}>
            <strong>{index + 1}:</strong> {label}
          </div>
        ))}
      </div>
    </div>
  );
};

export default BarChart;
