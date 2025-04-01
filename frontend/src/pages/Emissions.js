import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Bar, Pie } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from "chart.js";
import axios from 'axios';
import "../styles/Emissions.css";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Emissions = () => {
    const navigate = useNavigate();
    const location = useLocation();
    
    const state = location.state || {};
    const recipeName = state.recipeName || "Unnamed Recipe";
    const emissionsData = state.emissionsData || { breakdown: {}, total_emissions: 0 };
    const selectedIngredients = state.selectedIngredients || [];
    const matched_ingredients = state.matched_ingredients || {};

    const [error, setError] = useState(null);
    const [sustainabilityScore, setSustainabilityScore] = useState(null);

    useEffect(() => {
        if (!state.recipeName) {
            setError("Missing recipe data. Please try again.");
            return;
        }

        const matchedData = matched_ingredients[recipeName] || {};

        const requestData = {
            ingredients: selectedIngredients,
            land_use_change: matchedData["Land Use Change"] || 0,
            feed: matchedData["Feed"] || 0,
            farm: matchedData["Farm"] || 0,
            processing: matchedData["Processing"] || 0,
            transport: matchedData["Transport"] || 0,
            packaging: matchedData["Packaging"] || 0,
            retail: matchedData["Retail"] || 0,
            total_land_to_retail: matchedData["Total from Land to Retail"] || 0,
        };

        const fetchSustainabilityScore = async () => {
            try {
                const response = await axios.post('http://127.0.0.1:8000/predict', requestData);
                setSustainabilityScore(response.data.sustainability_score);
            } catch (error) {
                console.error('Error fetching sustainability score:', error);
                setSustainabilityScore('Error');
            }
        };

        fetchSustainabilityScore();
    }, [recipeName, emissionsData, selectedIngredients, matched_ingredients]);

    const emissionsBreakdown = emissionsData.breakdown;
    const totalEmissions = emissionsData.total_emissions;

    // Remove total emissions from the breakdown for the charts
    const filteredBreakdown = Object.entries(emissionsBreakdown).filter(([key, value]) => key !== "Total Emissions");
    const chartData = {
        labels: filteredBreakdown.map(([key]) => key),
        datasets: [
            {
                label: "Emissions (kg CO2)",
                data: filteredBreakdown.map(([, value]) => value),
                backgroundColor: ["#A2D2FF", "#FFAFCC", "#BDE0FE", "#FFBE98", "#B5E48C", "#FFCFD2"],
            },
        ],
    };

    // Function to determine color based on sustainability score
    const getScoreColor = (score) => {
        if (score >= 81) return "#2d6a4f"; // Green ✅
        if (score >= 61) return "#52b788"; // Light Green 🟢
        if (score >= 41) return "#ffcc00"; // Yellow 🟡
        if (score >= 21) return "#ff7f50"; // Orange 🟠
        return "#d9534f"; // Red 🔴
    };

    return (
        <div className="emissions-container">
            <h2>{recipeName}</h2>

            {error ? (
                <p className="error">{error}</p>
            ) : (
                <div className="emissions-content">
                    {/* Left Side: Sustainability Score */}
                    <div className="sustainability-score-container">
                        <h3>Sustainability Score</h3>
                        <div 
                            className="sustainability-score"
                            style={{ color: getScoreColor(sustainabilityScore) }}
                        >
                            {sustainabilityScore !== null ? sustainabilityScore : 'Calculating...'}
                        </div>
                    </div>

                    {/* Right Side: Emissions Data */}
                    <div className="emissions-data">
                        <h3>Emissions Breakdown</h3>
                        <ul>
                            {Object.entries(emissionsBreakdown).map(([key, value], index) => (
                                key !== "Total Emissions" && (
                                    <li key={index}>
                                        <strong>{key}:</strong> {value} kg CO2
                                    </li>
                                )
                            ))}
                        </ul>
                    </div>
                </div>
            )}

            {/* Charts */}
            <div className="emissions-chart">
                <div className="chart-container">
                    <h3>Bar Chart: Emissions by Category</h3>
                    <Bar data={chartData} options={{ responsive: true, plugins: { title: { display: true, text: "Emissions Breakdown" } } }} />
                </div>

                <div className="chart-container">
                    <h3>Pie Chart: Emissions Distribution</h3>
                    <Pie data={chartData} options={{ responsive: true, plugins: { title: { display: true, text: "Emissions Distribution" } } }} />
                </div>
            </div>

            <button onClick={() => navigate("/")}>Back to Search</button>
        </div>
    );
};

export default Emissions;
