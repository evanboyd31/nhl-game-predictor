// src/components/Header.js
import React from "react";
import "../styles/header.css";
import nhlLogo from "../assets/nhl-former-logo.svg";

const Header = () => {
  return (
    <header className="header">
      <a href="https://www.nhl.com" target="_blank" rel="noopener noreferrer">
        <img src={nhlLogo} alt="NHL Logo" className="nhl-logo" />
      </a>
      <h1 className="header-title">
        NHL Game Predictions <span className="header-emoji">🏒🥅</span>
      </h1>
    </header>
  );
};

export default Header;