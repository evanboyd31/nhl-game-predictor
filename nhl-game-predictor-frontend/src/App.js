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

  console.log(process.env.REACT_APP_BASE_API_URL);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGamePredictions = async () => {
      try {
        const todayInPacificTime = formatToPacificTime(
          new Date(),
          "yyyy-MM-dd"
        );
        const response = await fetch(
          `${process.env.REACT_APP_BASE_API_URL}game-predictions/date/?date=${todayInPacificTime}`
        );

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
        {error && (
          <div className="error-message">
            <span className="error-message-title">Error: </span>
            <span className="error-message-detail">{error}</span>
          </div>
        )}
        {!error && <GamePredictions gamePredictions={predictions} />}
      </div>
    </div>
  );
};

export default App;
