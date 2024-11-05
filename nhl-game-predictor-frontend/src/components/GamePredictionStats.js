import React from "react";
import GamePredictionBarChart from "./GamePredictionBarChart";

const GamePredictionStats = ({ gamePrediction, isOpen }) => {
  const winningTeamName = `${
    gamePrediction.predicted_home_team_win
      ? gamePrediction.game.home_team.name
      : gamePrediction.game.away_team.name
  }`;

  const topFeatures = gamePrediction.top_features;
  return isOpen?.isOpen ? (
    <div className="game-prediction-stats">
      <span className="game-prediction-stats-header">
        Our model predicts that the{" "}
        <span className="green-text">{winningTeamName}</span> will win today's
        game.
        <span>
          <br /> Here's why...
        </span>
      </span>
      <GamePredictionBarChart
        gamePrediction={gamePrediction}
        topFeatures={topFeatures}
        isOpen={isOpen}
      />
    </div>
  ) : null;
};

export default GamePredictionStats;
