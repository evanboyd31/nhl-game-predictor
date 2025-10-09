import "./index.css";
import Header from "./components/Header.js";
import GamePredictions from "./components/GamePredictions.js";
import Footer from "./components/Footer.js";
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
  const [loadingGamePredictions, setLoadingGamePredictions] = useState(true);

  // holds the error returned by the game predictions API endpoint
  const [gamePredictionsError, setGamePredicitonError] = useState(null);

  // game prediction model used for creating the loaded predictions
  const [predictionModel, setPredictionModel] = useState({});

  // whether the prediction model API has responded
  const [loadingPredictionModel, setLoadingPredictionModel] = useState(true);

  // holds the error returned by the prediction model API endpoint
  const [predictionModelError, setPredictionModelError] = useState(true);

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
          setGamePredicitonError(
            "Error: The prediction server is currently unavailable. Please try again later!"
          );
        } else {
          setGamePredicitonError(error.message);
        }
      } finally {
        setLoadingGamePredictions(false);
      }
    };

    fetchGamePredictions();

    const fetchPredictionModel = async () => {
      try {
        // send request to get prediction model JSON
        const response = await fetch(
          `${process.env.REACT_APP_BASE_API_URL}prediction-model/most-recent/`
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
        setPredictionModel(data);
      } catch (error) {
        // override the default "Faild to fetch" error message with a more descriptive one
        if (error.message === "Failed to fetch") {
          setPredictionModelError(
            "Error: The prediction server is currently unavailable. Please try again later!"
          );
        } else {
          setPredictionModelError(error.message);
        }
      } finally {
        setLoadingPredictionModel(false);
      }
    };

    fetchPredictionModel();
  }, []);

  useEffect(() => {
    console.log(`predictionModel: ${JSON.stringify(predictionModel)}`);
  }, [predictionModel]);

  return (
    <div className="app-container">
      <Header />
      <div className="page-body">
        {!gamePredictionsError && loadingGamePredictions && (
          <div className="spinner-container">
            <div className="spinner"></div>
          </div>
        )}
        {gamePredictionsError && !loadingGamePredictions && (
          <div className="error-message">
            <span className="error-message-title">Error: </span>
            <span className="error-message-detail">{gamePredictionsError}</span>
          </div>
        )}
        {!gamePredictionsError && !loadingGamePredictions && (
          <GamePredictions gamePredictions={predictions} />
        )}
      </div>
      <Footer />
    </div>
  );
};

export default App;
