import React from "react";
import { useState } from "react";
import "../styles/game-predictions.css";
import GamePrediction from "./GamePrediction";

const GamePredictions = ({ gamePredictions }) => {
  const today = new Date();
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
        Predictions for {today.toLocaleDateString()}
      </h3>
      <h4>Click on a game to see predictions!</h4>
      <ul className="game-predictions-list">
        {gamePredictions.map((gamePrediction) => {
          // default to closed if not found
          const isOpenPrediction = isOpen.find(
            (item) => item.id === gamePrediction.id
          ) || { isOpen: false };
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
