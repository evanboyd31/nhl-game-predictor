import React from "react";

const GamePrediction = ({ gamePrediction }) => {
  // extract relevant game info from Game, Team, GamePrediction objects
  const game = gamePrediction.game;
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
    <li className="item open">
      <h3 className="text">
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
    </li>
  );
};

export default GamePrediction;
