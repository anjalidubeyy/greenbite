import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bar, Pie } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import '../styles/CompareResults.css';

// Register all required Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend
);

const CompareResults = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { comparisonData } = location.state || {};

    if (!comparisonData) {
        return (
            <div className="error-container">
                <h2>No comparison data available</h2>
                <button onClick={() => navigate('/compare')}>Go Back</button>
            </div>
        );
    }

    const { dish1, dish2, comparison_result } = comparisonData;

    // Bar chart data for emissions comparison
    const emissionsChartData = {
        labels: ['Total Emissions'],
        datasets: [
            {
                label: dish1.title,
                data: [dish1.total_emissions],
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            },
            {
                label: dish2.title,
                data: [dish2.total_emissions],
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
            },
        ],
    };

    // Pie chart data for sustainability scores
    const sustainabilityChartData = {
        labels: [dish1.title, dish2.title],
        datasets: [
            {
                label: 'Sustainability Score',
                data: [dish1.sustainability_score, dish2.sustainability_score],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(255, 99, 132, 0.6)',
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 1,
            },
        ],
    };

    const barChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'CO₂e Emissions Comparison',
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'CO₂e (kg)',
                },
            },
        },
    };

    const pieChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Sustainability Score Comparison',
            },
        },
    };

    const renderIngredientsList = (ingredients) => (
        <ul className="ingredients-list">
            {ingredients.map((ing, index) => (
                <li key={index}>
                    {ing.name}: {ing.emission ? ing.emission.toFixed(2) : '0.00'} kg CO₂e
                </li>
            ))}
        </ul>
    );

    const moreEcoFriendly = dish1.sustainability_score > dish2.sustainability_score ? dish1.title : dish2.title;

    return (
        <div className="compare-results-container">
            <h1>Dish Comparison Results</h1>
            
            <div className="comparison-grid">
                <div className="dish-column">
                    <h2>{dish1.title}</h2>
                    <div className="score-box">
                        <h3>Sustainability Score</h3>
                        <p className="score">{dish1.sustainability_score.toFixed(1)}/5.0</p>
                    </div>
                    <div className="emissions-box">
                        <h3>Total Emissions</h3>
                        <p>{dish1.total_emissions.toFixed(2)} kg CO₂e</p>
                    </div>
                    <div className="equivalence-box">
                        <h3>Real-Life Equivalence</h3>
                        <ul className="equivalence-list">
                            <li>🚗 {dish1.emissions_equivalence.car_distance} km driven</li>
                            <li>📱 {dish1.emissions_equivalence.smartphone_charges} smartphone charges</li>
                            <li>🛍️ {dish1.emissions_equivalence.plastic_bags} plastic bags</li>
                            <li>💡 {dish1.emissions_equivalence.led_bulb_hours} hours of LED light</li>
                        </ul>
                    </div>
                    <div className="ingredients-box">
                        <h3>Ingredients</h3>
                        {renderIngredientsList(dish1.ingredients)}
                    </div>
                </div>

                <div className="dish-column">
                    <h2>{dish2.title}</h2>
                    <div className="score-box">
                        <h3>Sustainability Score</h3>
                        <p className="score">{dish2.sustainability_score.toFixed(1)}/5.0</p>
                    </div>
                    <div className="emissions-box">
                        <h3>Total Emissions</h3>
                        <p>{dish2.total_emissions.toFixed(2)} kg CO₂e</p>
                    </div>
                    <div className="equivalence-box">
                        <h3>Real-Life Equivalence</h3>
                        <ul className="equivalence-list">
                            <li>🚗 {dish2.emissions_equivalence.car_distance} km driven</li>
                            <li>📱 {dish2.emissions_equivalence.smartphone_charges} smartphone charges</li>
                            <li>🛍️ {dish2.emissions_equivalence.plastic_bags} plastic bags</li>
                            <li>💡 {dish2.emissions_equivalence.led_bulb_hours} hours of LED light</li>
                        </ul>
                    </div>
                    <div className="ingredients-box">
                        <h3>Ingredients</h3>
                        {renderIngredientsList(dish2.ingredients)}
                    </div>
                </div>
            </div>

            <div className="charts-container">
                <div className="chart-container">
                    <h3>Emissions Comparison</h3>
                    <div className="chart-wrapper">
                        <Bar data={emissionsChartData} options={barChartOptions} />
                    </div>
                </div>
                
                <div className="chart-container">
                    <h3>Sustainability Score Comparison</h3>
                    <div className="chart-wrapper">
                        <Pie data={sustainabilityChartData} options={pieChartOptions} />
                    </div>
                </div>
            </div>

            <div className="comparison-result">
                <h2>Comparison Result</h2>
                <p className="result-message">{comparison_result}</p>
            </div>

            <div className="conclusion">
                <p><strong>{moreEcoFriendly}</strong> is the more eco-friendly choice! 🌱</p>
            </div>

            <div className="actions">
                <button onClick={() => navigate('/compare')}>Compare More Dishes</button>
                <button onClick={() => navigate('/')}>Back to Home</button>
            </div>
        </div>
    );
};

export default CompareResults; 