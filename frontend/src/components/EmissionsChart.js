import React from "react";
import { Bar, Pie} from "react-chartjs-2";
import "chart.js/auto";
import "../styles/Emissions.css";

const EmissionsChart = ({ emissionsData }) => {
    if (!emissionsData || !emissionsData.breakdown) return <p>No data available</p>;

    const labels = Object.keys(emissionsData.breakdown).filter(label => label !== "Total Emissions");
    const values = labels.map(label => emissionsData.breakdown[label]);
    
    const pastelColors = ["#FFB6C1", "#98FB98", "#FFDAB9", "#B0E0E6", "#F5DEB3", "#E6E6FA", "#D8BFD8"];

    const barData = {
        labels,
        datasets: [{
            label: "Emissions (kg CO₂e)",
            data: values,
            backgroundColor: pastelColors,
            borderRadius: 8,
        }],
    };

    const pieData = {
        labels,
        datasets: [{
            data: values,
            backgroundColor: pastelColors,
            hoverOffset: 8,
        }],
    };

    return (
        <div className="emissions-charts">
            <h2>🌱 Emissions Breakdown</h2>
            <div className="chart-container">
                <div className="chart-box">
                    <h3>Bar Chart</h3>
                    <Bar data={barData} options={{ responsive: true }} />
                </div>
                <div className="chart-box">
                    <h3>Pie Chart</h3>
                    <Pie data={pieData} options={{ responsive: true }} />
                </div>
            </div>
        </div>
    );
};

export default EmissionsChart;
