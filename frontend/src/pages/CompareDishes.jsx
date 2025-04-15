import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/CompareDishes.css';

const CompareDishes = () => {
    const [dish1, setDish1] = useState('');
    const [dish2, setDish2] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        console.log('CompareDishes component mounted');
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch('http://localhost:5000/compare-dishes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ dish1, dish2 }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            navigate('/compare-results', { state: { comparisonData: data } });
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to compare dishes. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="compare-dishes-container">
            <h1>Compare Dishes</h1>
            <p>Enter two dishes to compare their environmental impact</p>
            
            <form onSubmit={handleSubmit} className="compare-form">
                <div className="search-container">
                    <div className="search-box">
                        <label htmlFor="dish1">First Dish</label>
                        <input
                            type="text"
                            id="dish1"
                            value={dish1}
                            onChange={(e) => setDish1(e.target.value)}
                            placeholder="Enter first dish name"
                            required
                        />
                    </div>

                    <div className="search-box">
                        <label htmlFor="dish2">Second Dish</label>
                        <input
                            type="text"
                            id="dish2"
                            value={dish2}
                            onChange={(e) => setDish2(e.target.value)}
                            placeholder="Enter second dish name"
                            required
                        />
                    </div>
                </div>

                <button 
                    type="submit" 
                    className="compare-button"
                    disabled={loading || !dish1 || !dish2}
                >
                    {loading ? 'Comparing...' : 'Compare Dishes'}
                </button>
            </form>
        </div>
    );
};

export default CompareDishes; 