import React from "react";
import GamePredictionBarChart from "./GamePredictionBarChart";
import GamePredictionConfidence from "./GamePredictionConfidence";

/**
 * The GamePredictionStats component is a container that
 * displays the name of the winning team and holds the importances
 * GamePredictionBarChart, only when the parent GamePrediction
 * component has been opened
 */
const GamePredictionStats = ({ gamePrediction, isOpen }) => {
  const winningTeamName = `${
    gamePrediction.predicted_home_team_win
      ? gamePrediction.game.home_team.name
      : gamePrediction.game.away_team.name
  }`;

  const confidenceLevel = Math.round(gamePrediction.confidence_score * 100);

  const topFeatures = gamePrediction.top_features;
  return isOpen?.isOpen ? (
    <div className="game-prediction-stats">
      <span className="game-prediction-stats-header">
        Our model predicts that the{" "}
        <span className="green-text">{winningTeamName}</span> will win today's
        game with a certainty of{" "}
        <span className="green-text">{confidenceLevel}%</span>.
      </span>
      <GamePredictionConfidence
        gamePrediction={gamePrediction}
        isOpen={isOpen}
      />
      <span className="game-prediction-stats-header">
        <br />
        <br /> Here's why...
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
