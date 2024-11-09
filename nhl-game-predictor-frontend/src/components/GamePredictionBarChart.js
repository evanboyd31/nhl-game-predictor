import React from "react";
import { Bar } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";

// register chart js so components can be used
Chart.register(...registerables);

/**
 * Given a game prediction, extract the game prediction data
 * into legend labels, original labels, and importances for the
 * GamePredictionBarChart component
 */
const extractGamePredictionData = (gamePrediction) => {
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

const GamePredictionBarChart = ({ gamePrediction }) => {
  const { legendLabels, originalLabels, importances } =
    extractGamePredictionData(gamePrediction);

  // set the chart data for the Bar chart.js component
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

  // options for the Bar chart.js component
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
      datalabels: false,
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

export default GamePredictionBarChart;
