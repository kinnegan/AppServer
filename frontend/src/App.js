import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { DataProvider } from "./context/DataContext";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import "./styles.css";

const App = () => (
  <DataProvider>
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  </DataProvider>
);

export default App;
