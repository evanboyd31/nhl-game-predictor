import React from "react";
import GamePredictionBarChart from "./GamePredictionBarChart";

const GamePredictionStats = ({ gamePrediction, isOpen }) => {
  const winnerString = `${
    gamePrediction.predicted_home_team_win
      ? gamePrediction.game.home_team.name
      : gamePrediction.game.away_team.name
  }`;

  const teamName = winnerString.split(" ").slice(1).join(" ");
  console.log(teamName);

  const topFeatures = gamePrediction.top_features;
  return isOpen.isOpen ? (
    <div className="game-prediction-stats">
      <span className="game-prediction-stats-header">
        <span className="green-text">Predicted winner:</span>{" "}
        <span>
          {teamName}. <br /> Here's why...
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
