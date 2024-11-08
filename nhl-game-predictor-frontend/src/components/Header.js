// src/components/Header.js
import React from "react";
import "../styles/header.css";
import nhlLogo from "../assets/nhl-former-logo.svg";

/**
 * The Header component contains the page title, an NHL logo,
 * and a hockey emoji, and is placed at the top of all pages on the
 * frontend
 */
const Header = () => {
  return (
    <header className="header">
      <a href="https://www.nhl.com" target="_blank" rel="noopener noreferrer">
        <img src={nhlLogo} alt="NHL Logo" className="nhl-logo" />
      </a>
      <h1 className="header-title">
        Predictions
        <span className="header-emoji">🏒</span>
      </h1>
    </header>
  );
};

export default Header;
