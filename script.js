document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Mobile Menu Toggle ---
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });

    // Close menu when a link is clicked
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });

    // --- 2. Cost Calculator Logic ---
    const costForm = document.getElementById('costForm');
    const resultBox = document.getElementById('resultBox');
    const totalPriceDisplay = document.getElementById('totalPrice');

    // Rates per square foot (in Currency)
    const rates = {
        economy: 1200,
        standard: 1600,
        premium: 2200,
        luxury: 3000
    };

    costForm.addEventListener('submit', (e) => {
        e.preventDefault(); // Stop page from reloading

        // Get values from inputs
        const area = parseFloat(document.getElementById('area').value);
        const quality = document.getElementById('quality').value;
        const floors = parseInt(document.getElementById('floors').value);

        if (area && floors) {
            // Calculation Formula: Area * Rate * Floors
            const rate = rates[quality];
            const totalCost = area * rate * floors;

            // Format Number (e.g., 2500000 -> 2,500,000)
            const formattedCost = totalCost.toLocaleString('en-IN');

            // Show Result
            totalPriceDisplay.innerText = "₹" + formattedCost;
            resultBox.classList.remove('hidden');
        }
    });
});