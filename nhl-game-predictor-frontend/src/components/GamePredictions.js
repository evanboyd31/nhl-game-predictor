import React from "react";
import "../styles/game-predictions.css";
import GamePrediction from "./GamePrediction";
import gamePredictions from "./TestData";

const formatDate = (date) => {
  const options = { month: "long", day: "numeric", year: "numeric" };
  const day = date.getDate();
  const suffix = day === 1 ? "st" : day === 2 ? "nd" : day === 3 ? "rd" : "th";
  return `${date
    .toLocaleString("default", options)
    .replace(day, day + suffix)}`;
};

const GamePredictions = () => {
  return (
    <div className="game-predictions">
      <h3 className="game-predictions-header">
        Predictions for games on {formatDate(new Date())}
      </h3>
      <ul className="game-predictions-list">
        {gamePredictions.map((gamePrediction) => (
          <GamePrediction gamePrediction={gamePrediction} />
        ))}
      </ul>
    </div>
  );
};

export default GamePredictions;
