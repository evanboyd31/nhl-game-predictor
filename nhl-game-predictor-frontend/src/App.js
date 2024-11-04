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
          throw new Error("Network response was not ok");
        }

        const data = await response.json();
        setPredictions(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchGamePredictions();
  }, []);

  // display loading text if we need to wait
  if (loading) {
    return <div>Loading...</div>;
  }

  // display error text if an error is returned
  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="app-container">
      <Header />
      <div className="page-body">
        <GamePredictions gamePredictions={predictions} />
      </div>
    </div>
  );
};

export default App;
