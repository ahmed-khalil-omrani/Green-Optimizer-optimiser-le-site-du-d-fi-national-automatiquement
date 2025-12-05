import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import './GreenOptimizer.css';

const GreenOptimizer = () => {
    const [theme, setTheme] = useState('light');

    useEffect(() => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) {
            setTheme(storedTheme);
            document.body.className = storedTheme === 'dark' ? 'dark-mode' : 'light-mode';
        } else {
            document.body.className = 'light-mode';
        }
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        document.body.className = newTheme === 'dark' ? 'dark-mode' : 'light-mode';
    };

    return (
        <div className={`app-container ${theme}-mode`}>
            <div className="theme-switch-container">
                <button
                    id="theme-toggle"
                    className="theme-toggle"
                    aria-label="Basculer le thème"
                    onClick={toggleTheme}
                >
                    <i className={`fas ${theme === 'light' ? 'fa-moon' : 'fa-sun'}`}></i>
                </button>
            </div>

            <Outlet />
        </div>
    );
};

export default GreenOptimizer;
