import React from "react";
import GamePredictionStats from "./GamePredictionStats";

/**
 * The GamePrediction component is the individual component displayed for
 * each of the NHL games schedule on a current day. The GamePrediction
 * component can be clicked on, which will expand the div and show the
 * predicted winner and related statistics in a GamePredictionStats
 * component
 */
const GamePrediction = ({ gamePrediction, isOpen, onGamePredictionClick }) => {
  // extract relevant game info from Game, Team, GamePrediction objects
  const game = gamePrediction.game;
  const gamePredictionId = gamePrediction.id;
  const gameJson = game.game_json;

  // home team info
  const homeTeamName = game.home_team.name;
  const homeTeamAbbreviation = game.home_team.abbreviation;
  const homeTeamDarkLogoURL = gameJson.homeTeam.darkLogo;

  // away team info
  const awayTeamName = game.away_team.name;
  const awayTeamAbbreviation = game.away_team.abbreviation;
  const awayTeamDarkLogoURL = gameJson.awayTeam.darkLogo;

  return (
    <li
      className={`item ${isOpen?.isOpen ? "open" : ""}`}
      onClick={() => onGamePredictionClick(gamePredictionId)}
    >
      <h3 className="game-prediction-header">
        <span>{awayTeamAbbreviation}</span> at{" "}
        <span>{homeTeamAbbreviation}</span>
      </h3>

      <div className="team-logos">
        <img
          src={awayTeamDarkLogoURL}
          alt={`${awayTeamName} Logo`}
          className="team-logo away-team-logo"
        />
        <img
          src={homeTeamDarkLogoURL}
          alt={`${homeTeamName} Logo`}
          className="team-logo home-team-logo"
        />
      </div>

      {isOpen?.isOpen && (
        <GamePredictionStats gamePrediction={gamePrediction} isOpen={isOpen} />
      )}
    </li>
  );
};

export default GamePrediction;
