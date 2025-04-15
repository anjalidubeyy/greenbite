import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Results from "./pages/Results";
import Emissions from "./pages/Emissions";
import CompareDishes from "./pages/CompareDishes";
import CompareResults from "./pages/CompareResults";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/results" element={<Results />} />
                <Route path="/emissions" element={<Emissions />} />
                <Route path="/compare" element={<CompareDishes />} />
                <Route path="/compare-results" element={<CompareResults />} />
            </Routes>
        </Router>
    );
};

export default App;
