import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import "../styles/prediction-model.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * The PredictionModel component displays a horizontal bar chart
 * of feature importances for the current prediction model.
 * The chart is sorted in descending order of importance.
 */
const PredictionModel = ({ predictionModel }) => {
  if (!predictionModel || !predictionModel.feature_importances) {
    console.log(`made it here`);
    return null;
  }

  // Convert feature importances object to array and sort descending
  const sortedFeatures = Object.entries(
    predictionModel.feature_importances
  ).sort((a, b) => b[1] - a[1]);

  const labels = sortedFeatures.map(([feature]) => feature);
  const importances = sortedFeatures.map(([_, importance]) =>
    importance.toFixed(3)
  );

  const data = {
    labels,
    datasets: [
      {
        label: "Feature Importance",
        data: importances,
        color: "rgba(255, 255, 255, 1)",
        backgroundColor: "rgba(238, 152, 58, 0.6)",
        borderColor: "rgba(238, 152, 58, 1)",
        borderWidth: 1,
      },
    ],
  };

  const options = {
    indexAxis: "y", // horizontal bar chart
    responsive: true,
    maintainAspectRato: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: `${predictionModel.name} (v${predictionModel.version}) Feature Importances`,
        font: {
          size: 16,
          family: "Arial",
          weight: "bold",
        },
        color: "#FFFFFF",
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.dataset.label}: ${context.raw}`;
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "Importance",
          font: { size: 13 },
          color: "#FFFFFF",
        },
        ticks: {
          callback: (value) => value.toFixed(3),
          color: "#FFFFFF",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
      },
      y: {
        title: {
          display: true,
          text: "Feature",
          font: { size: 13 },
          color: "#FFFFFF",
        },
        ticks: {
          autoSkip: false,
          color: "#FFFFFF",
          font: {
            size: 10,
          },
        },
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },

        barPercentage: 0.6,
        categoryPercentage: 0.7,
      },
    },
  };

  return (
    <div className="prediction-model-container">
      <h3 className="prediction-model-header">Prediction Model Details</h3>
      <p className="prediction-model-description">
        Trained on seasons:{" "}
        {predictionModel.trained_seasons?.join(", ") || "N/A"}
      </p>
      <div
        className="prediction-model-chart"
        style={{ height: `${labels.length * 35}px` }}
      >
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default PredictionModel;
