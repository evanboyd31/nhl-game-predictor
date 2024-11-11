import React from "react";
import "../styles/footer.css";
import githubLogo from "../assets/github.svg";

const Footer = () => {
  return (
    <footer className="footer">
      <a
        href="https://github.com/evanboyd31/nhl-game-predictor"
        target="_blank"
        rel="noopener noreferrer"
      >
        <img src={githubLogo} alt="Github link" className="nhl-logo" />
      </a>
    </footer>
  );
};

export default Footer;
