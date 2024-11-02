import React from "react";
import { useState } from "react";
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
  const [isOpen, setIsOpen] = useState(
    gamePredictions.map((gamePrediction) => ({
      id: gamePrediction.id,
      isOpen: false,
    }))
  );

  const handleGamePredictionClick = (gamePredictionId) => {
    setIsOpen(
      isOpen.map((gamePrediction) =>
        gamePredictionId === gamePrediction.id
          ? { ...gamePrediction, isOpen: !gamePrediction.isOpen }
          : { ...gamePrediction, isOpen: false }
      )
    );
  };

  return (
    <div className="game-predictions">
      <h3 className="game-predictions-header">
        Predictions for games on {formatDate(new Date())}
      </h3>
      <ul className="game-predictions-list">
        {gamePredictions.map((gamePrediction) => {
          const isOpenPrediction = isOpen.find(
            (item) => item.id === gamePrediction.id
          );
          return (
            <GamePrediction
              gamePrediction={gamePrediction}
              key={gamePrediction.id}
              isOpen={isOpenPrediction}
              onGamePredictionClick={handleGamePredictionClick}
            />
          );
        })}
      </ul>
    </div>
  );
};

export default GamePredictions;
