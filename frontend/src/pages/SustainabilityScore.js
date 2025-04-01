import { useState, useEffect } from "react";

const SustainabilityScore = ({ emissionsData }) => {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (emissionsData) {
      fetchSustainabilityScore(emissionsData);
    }
  }, [emissionsData]);

  const fetchSustainabilityScore = async (data) => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch sustainability score");
      }

      const result = await response.json();
      setScore(result.sustainability_score);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sustainability-score-container">
      <h2>Sustainability Score</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: "red" }}>{error}</p>
      ) : score !== null ? (
        <p className="score">🌍 Score: <strong>{score}</strong></p>
      ) : (
        <p>No data available</p>
      )}
    </div>
  );
};

export default SustainabilityScore;
