import React from "react";

const GamePredictionStats = ({ gamePrediction }) => {
  const winnerString = `${
    gamePrediction.predicted_home_team_win
      ? gamePrediction.game.home_team.name
      : gamePrediction.game.away_team.name
  }`;

  return (
    <div className="game-prediction-stats">
      <span className="game-prediction-stats-header">
        <span className="green-text">Predicted winner:</span>{" "}
        <span>{winnerString}. Here's why...</span>
      </span>
      <ul></ul>
    </div>
  );
};

export default GamePredictionStats;
