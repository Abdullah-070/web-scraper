// Navigation & Lifecycle Management Configuration
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Event Listeners
    const loginForm = document.getElementById('loginForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const dropdownLogout = document.getElementById('dropdownLogout');
    
    const menuDashboard = document.getElementById('menu-dashboard');
    const menuScrapers = document.getElementById('menu-scrapers');
    const viewAllRecent = document.getElementById('viewAllRecent');

    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
    if (dropdownLogout) dropdownLogout.addEventListener('click', handleLogout);

    if (menuDashboard) menuDashboard.addEventListener('click', (e) => { e.preventDefault(); navigateTo('dashboard'); });
    if (menuScrapers) menuScrapers.addEventListener('click', (e) => { e.preventDefault(); navigateTo('scrapers'); });
    if (viewAllRecent) viewAllRecent.addEventListener('click', (e) => { e.preventDefault(); navigateTo('scrapers'); });
});

// Switch view logic

    function handleLogin(event) {
    event.preventDefault(); // Page reload hone se rokne ke liye

    // Selecting the values of email and pssword
    const emailInput = document.querySelector('input[type="email"]').value;
    const passwordInput = document.querySelector('input[type="password"]').value;
    const errorDiv = document.getElementById('login-error');

    // Sahi credentials set karna
    const correctEmail = "admin@sanestix.com";
    const correctPassword = "password123";

    if (emailInput === correctEmail && passwordInput === correctPassword) {
        // credentials Right
        if (errorDiv) {
            errorDiv.style.display = 'none'; // Hide the error
        }
        document.getElementById('login-screen').classList.add('d-none');
        document.getElementById('app-container').style.display = 'flex';
        renderChart(); // Graph load karein
    } else {
        // Agar galat hain toh error message show karein(Wrong Credential throw this statement)
        if (errorDiv) {
            errorDiv.style.display = 'block';
        }
    }
}
  
function handleLogout(event) {
    event.preventDefault();
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('login-screen').classList.remove('d-none');
}

function navigateTo(viewName) {
    // Toggle application pages
    document.getElementById('dashboard-view').classList.add('d-none');
    document.getElementById('scrapers-view').classList.add('d-none');

    // Update active visual cues on sidebar menu
    document.getElementById('menu-dashboard').classList.remove('active');
    document.getElementById('menu-scrapers').classList.remove('active');

    if (viewName === 'dashboard') {
        document.getElementById('dashboard-view').classList.remove('d-none');
        document.getElementById('menu-dashboard').classList.add('active');
    } else if (viewName === 'scrapers') {
        document.getElementById('scrapers-view').classList.remove('d-none');
        document.getElementById('menu-scrapers').classList.add('active');
    }
}

// Chart.js instance config
let jobChartInstance = null;
function renderChart() {
    const canvasElement = document.getElementById('jobsChart');
    if (!canvasElement) return;

    const ctx = canvasElement.getContext('2d');
    if (jobChartInstance) {
        jobChartInstance.destroy();
    }
    
    jobChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jul 05', 'Jul 06', 'Jul 07', 'Jul 08', 'Jul 09', 'Jul 10', 'Jul 11'],
            datasets: [
                {
                    label: 'Completed',
                    data: [13, 28, 27, 45, 28, 23, 29],
                    borderColor: '#22C55E',
                    backgroundColor: 'transparent',
                    borderWidth: 2.5,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#22C55E'
                },
                {
                    label: 'Failed',
                    data: [2, 13, 5, 13, 10, 4, 8],
                    borderColor: '#EF4444',
                    backgroundColor: 'transparent',
                    borderWidth: 2.5,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#EF4444'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false // Display custom DOM legends
                }
            },
            scales: {
                y: {
                    border: { dash: [5, 5] },
                    grid: {
                        color: '#E2E8F0'
                    },
                    ticks: {
                        color: '#64748B',
                        font: { family: 'Inter', size: 11 }
                    },
                    min: 0,
                    max: 50
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#64748B',
                        font: { family: 'Inter', size: 11 }
                    }
                }
            }
        }
    });
}