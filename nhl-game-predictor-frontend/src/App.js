import "./index.css";
import Header from "./components/Header.js";
import GamePredictions from "./components/GamePredictions.js";

const App = () => {
  return (
    <div className="app-container">
      <Header />
      <div className="page-body">
        <GamePredictions />
      </div>
    </div>
  );
};

export default App;
