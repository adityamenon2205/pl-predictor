import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/layout/Layout";

import Overview from "./pages/Overview";
import Teams from "./pages/Teams";
import About from "./pages/About";
import Predictor from "./pages/Predictor";
import Analytics from "./pages/Analytics";
import History from "./pages/History";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Overview />} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/predict" element={<Predictor />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/history" element={<History />} />
          <Route path="/about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;