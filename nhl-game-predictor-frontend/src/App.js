import "./index.css";
import Header from "./components/Header.js";
import GamePredictions from "./components/GamePredictions.js";
import { useState, useEffect } from "react";
import formatToPacificTime from "./utils/timeUtils.js";

const App = () => {
  // set page title
  useEffect(() => {
    document.title = "NHL Game Predictions";
  }, []);

  // game predictions for the requested date
  const [predictions, setPredictions] = useState([]);

  // whether the game predictions API has responded
  const [loading, setLoading] = useState(true);

  // holds the error returned by the game predictions API endpoint
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGamePredictions = async () => {
      try {
        // the REST API operates in Pacific Time, so request the current day in pacific time
        const todayInPacificTime = formatToPacificTime(
          new Date(),
          "yyyy-MM-dd"
        );
        const response = await fetch(
          `${process.env.REACT_APP_BASE_API_URL}game-predictions/date/?date=${todayInPacificTime}`
        );

        // throw a custom error message that is more clear when the REST API endpoint doesn't reply
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData && errorData.detail
              ? errorData.detail
              : "The prediction server is currently unavailable. Please try again later!"
          );
        }

        const data = await response.json();
        setPredictions(data);
      } catch (error) {
        // override the default "Faild to fetch" error message with a more descriptive one
        if (error.message === "Failed to fetch") {
          setError(
            "Error: The prediction server is currently unavailable. Please try again later!"
          );
        } else {
          setError(error.message);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchGamePredictions();
  }, []);

  return (
    <div className="app-container">
      <Header />
      <div className="page-body">
        {!error && loading && (
          <div className="spinner-container">
            <div className="spinner"></div>
          </div>
        )}
        {error && !loading && (
          <div className="error-message">
            <span className="error-message-title">Error: </span>
            <span className="error-message-detail">{error}</span>
          </div>
        )}
        {!error && !loading && (
          <GamePredictions gamePredictions={predictions} />
        )}
      </div>
    </div>
  );
};

export default App;
