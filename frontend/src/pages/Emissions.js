import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import "../styles/Emissions.css";
import EmissionsChart from "../components/EmissionsChart";

const Emissions = () => {
    const location = useLocation();
    const [emissionsData, setEmissionsData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const selectedIngredients = location.state?.ingredients || [];

    useEffect(() => {
        if (selectedIngredients.length === 0) return;

        const fetchEmissions = async () => {
            setLoading(true);
            setError(null);

            try {
                const cleanedIngredients = selectedIngredients.map(ing => ing.replace(/[\"\[\]]/g, "").trim());

                const response = await fetch("http://localhost:5000/emissions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ingredients: cleanedIngredients }),
                });

                if (!response.ok) throw new Error(`API Error: ${response.status}`);

                const data = await response.json();
                console.log("✅ API Response:", data);
                console.log("🔍 Breakdown Data:", data.breakdown);

                if (data.breakdown && Object.keys(data.breakdown).length > 0) {
                    setEmissionsData({
                        breakdown: data.breakdown,
                        total_emissions: data.total_emissions,
                    });
                    console.log("✅ EmissionsData Updated:", data);
                } else {
                    console.log("❌ No valid breakdown received, setting empty state.");
                    setEmissionsData(null);
                }
            } catch (err) {
                console.error("❌ Error Fetching Emissions:", err);
                setError(err.message);
                setEmissionsData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchEmissions();
    }, [selectedIngredients]);

    return (
        <div className="emissions-container">
            <h2>🌱 Emissions Report</h2>

            {console.log("🔎 Debugging Render: ", emissionsData)}

            {loading && <p>Loading emissions data...</p>}
            {error && <p className="error">⚠ Error: {error}</p>}

            {emissionsData && emissionsData.breakdown && (
                <div className="emissions-content">
                    {/* Emissions Data */}
                    <div className="emissions-data">
                        <p>Total Emissions: {emissionsData.total_emissions.toFixed(2)} kg CO₂e</p>
                        <ul>
                            {Object.entries(emissionsData.breakdown).map(([key, value]) => (
                                <li key={key}>{key}: {value.toFixed(3)} kg CO₂e</li>
                            ))}
                        </ul>
                    </div>

                    {/* Emissions Chart */}
                    <div className="emissions-chart">
                        <EmissionsChart emissionsData={emissionsData} />
                    </div>
                </div>
            )}

            {!loading && !error && (!emissionsData?.breakdown || Object.values(emissionsData.breakdown).every(val => val === 0)) && (
                <p className="error">⚠ No emissions data available.</p>
            )}
        </div>
    );
};

export default Emissions;
