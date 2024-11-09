// GamePredictionConfidence.js
import React, { useRef, useEffect } from "react";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";

Chart.register(ChartDataLabels);

const GamePredictionConfidence = ({ gamePrediction, isOpen }) => {
  const confidenceLevel = Math.round(gamePrediction.confidence_score * 100);
  const canvasRef = useRef(null);
  const chartRef = useRef(null); // Ref to store the chart instance

  useEffect(() => {
    // Destroy any existing chart instance before creating a new one
    if (chartRef.current) {
      chartRef.current.destroy();
    }

    const ctx = canvasRef.current.getContext("2d");

    // Create new chart instance and store it in chartRef
    chartRef.current = new Chart(ctx, {
      type: "doughnut",
      data: {
        datasets: [
          {
            data: [confidenceLevel, 100 - confidenceLevel],
            backgroundColor: ["#328e44", "#FFFFFF"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        cutout: "85%",
        rotation: 0,
        plugins: {
          tooltip: { enabled: false },
          datalabels: {
            display: false,
            formatter: () => `${confidenceLevel}%`,
            color: "#328e44",
            font: {
              weight: "bold",
              size: 18,
            },
            anchor: "center", // Center the label within the chart
            align: "center", // Align the label to the center of its position
          },
        },
      },
    });

    // Cleanup function to destroy chart instance when component unmounts or updates
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [confidenceLevel]); // Re-run effect if confidenceLevel changes

  return (
    <div style={{ position: "relative", width: "200px", height: "200px" }}>
      <canvas ref={canvasRef} width={120} height={120} />
      <div
        style={{
          position: "absolute",
          top: "55%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          color: "#328e44",
          fontSize: "18px",
          fontWeight: "bold",
        }}
      >
        {`${confidenceLevel}%`}
      </div>
    </div>
  );
};

export default GamePredictionConfidence;
