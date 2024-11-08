import React from "react";
import { useState } from "react";
import "../styles/game-predictions.css";
import GamePrediction from "./GamePrediction";
import formatToPacificTime from "../utils/timeUtils";

/**
 * The GamePredictions component is the vertical component that contains each
 * GamePrediction component for the selected date.
 */
const GamePredictions = ({ gamePredictions }) => {
  // the timezone of the backend and the frontend is Pacific Time
  const todayInPacificTime = formatToPacificTime(new Date(), "yyyy-MM-dd");
  const [isOpen, setIsOpen] = useState(
    gamePredictions.map((gamePrediction) => ({
      id: gamePrediction.id,
      isOpen: false,
    }))
  );

  /**
   * The handleGamePredictionClick function will set the isOpen
   * state of the clicked GamePrediction to true so that relevant
   * GamePrediction data is displayed to the user
   * @param {Number} gamePredictionId - ID of GamePrediction object that had its corresponding div clicked
   */
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
        Predictions for {todayInPacificTime}
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
