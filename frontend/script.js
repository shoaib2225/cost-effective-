/* f:\fyp shoaib\script.js */

function scrollToAnalyzer() {
    document.getElementById('analyzer').scrollIntoView({ behavior: 'smooth' });
}

function goToAnalyzer() {
    const query = document.getElementById('headerSearch').value;
    window.location.href = `ai_response.html?q=${encodeURIComponent(query)}`;
}

function handleSearch() {
    const query = document.getElementById('medSearch').value.toLowerCase();
    const resultsContainer = document.getElementById('resultsGrid');
    
    if (query.trim() === "") {
        resultsContainer.innerHTML = '<div class="placeholder-msg">Enter a medicine name to synchronize clinical data.</div>';
        return;
    }
}

const API_BASE = "http://127.0.0.1:8000";

async function runAnalysis() {
    const query = document.getElementById('medSearch').value.toLowerCase();
    const resultsContainer = document.getElementById('resultsGrid');
    
    if (!query) return;

    // Premium UI Shift: Move existing items or clear
    resultsContainer.innerHTML = '<div class="analyzer-loading">⚙️ Synchronizing Clinical Data Node...</div>';
    
    // Artificial delay for 'AI feeling'
    await new Promise(resolve => setTimeout(resolve, 800));

    // Search in DB
    try {
        const res = await fetch(`${API_BASE}/api/medicines/search?q=${encodeURIComponent(query)}`);
        const results = await res.json();

        if (results && results.length > 0) {
            resultsContainer.innerHTML = ''; // Clear container
            results.forEach(med => {
                renderMedResult(med);
            });
            
            // Optimized "Move Up" effect: Force-scroll the AI Suggested Card into better view
            setTimeout(() => {
                const aiCard = document.getElementById('ai-suggested-card');
                if (aiCard) {
                    aiCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }, 100);
        } else {
            resultsContainer.innerHTML = `
                <div class="placeholder-msg">
                    Target Molecule not found in current local registry. 
                    <br><br>
                    💡 Try searching for: <b>Lipitor</b>, <b>Augmentin</b>, or <b>Zovirax</b>.
                </div>`;
        }
    } catch (err) {
        console.error(err);
        resultsContainer.innerHTML = `<div class="placeholder-msg">Error synchronizing clinical data.</div>`;
    }
}

function renderMedResult(med) {
    const resultsContainer = document.getElementById('resultsGrid');
    const alt = med.alternatives[0]; // Take primary alternative for visualization as in the image
    
    const cardHtml = `
        <!-- Current Source Card -->
        <div class="comp-card" style="cursor: pointer;" onclick="window.location.href='pharmacy_map.html?med=' + encodeURIComponent('${med.name}') + '&pharmacy=Local Pharmacy'" title="Click to view pharmacies with this medicine">
            <div class="card-header">
                <span class="tag-badge" style="background: rgba(255,255,255,0.05); color: #64748b;">CURRENT SOURCE</span>
                <span class="tag-badge" style="background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444;">ORIGINAL PRICE</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h3 style="font-family: 'Outfit'; font-size: 2rem; font-weight: 800;">${med.name}</h3>
                <span class="price-main">Rs. ${parseFloat(med.price).toLocaleString()}</span>
            </div>
            <div class="progress-container">
                <div class="progress-label">
                    <span>COST INDEX</span>
                    <span>HIGH (RED)</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: 85%; background: #ef4444;"></div>
                </div>
            </div>

            <!-- Locator Lead Button for Current Source -->
            <button class="btn-run" style="width: 100%; margin-top: 2rem; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); color: #ef4444;">
                📍 Locate Nearby Pharmacy →
            </button>
        </div>

        <!-- AI Suggested Alternative Card -->
        <div class="comp-card" id="ai-suggested-card" style="cursor: pointer;" onclick="window.location.href='pharmacy_map.html?med=' + encodeURIComponent('${alt.name}') + '&pharmacy=' + encodeURIComponent('${alt.pharmacy}')" title="Click to view pharmacies with this alternative">
            <div class="card-header">
                <span class="tag-badge" style="background: rgba(0, 102, 255, 0.1); color: #0066ff;">AI SUGGESTED ALTERNATIVE</span>
                <span class="tag-badge" style="background: rgba(0, 242, 255, 0.1); color: #00f2ff; border: 1px solid #00f2ff;">OPTIMAL PRICE</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h3 style="font-family: 'Outfit'; font-size: 2rem; font-weight: 800;">${alt.name}</h3>
                <span class="price-main">Rs. ${parseFloat(alt.price).toLocaleString()}</span>
            </div>
            <div style="margin-bottom: 2rem; color: #64748b; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
                <span class="icon">🏢</span> Available via: <strong>${alt.pharmacy}</strong>
            </div>
            <div class="progress-container">
                <div class="progress-label">
                    <span>COST INDEX</span>
                    <span>${Math.round((alt.price/med.price)*100)}% OPTIMAL</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: ${Math.round((alt.price/med.price)*100)}%; background: #0066ff; box-shadow: 0 0 10px #0066ff;"></div>
                </div>
            </div>
            
            <!-- Locator Lead Button -->
            <button class="btn-run" style="width: 100%; margin-top: 2rem; background: rgba(0, 102, 255, 0.1); border: 1px solid rgba(0, 102, 255, 0.3); color: #0066ff;">
                📍 Locate Nearby Pharmacy →
            </button>
        </div>
    `;
    
    resultsContainer.insertAdjacentHTML('beforeend', cardHtml);
}

// --- AUTHENTICATION & UI LOGIC --- //

async function handleLogin(e) {
    if (e) e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = e.target.querySelector('button');
    const origText = btn.innerText;
    
    btn.innerText = "⏳ Authenticating...";
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('auth', 'true');
            localStorage.setItem('user', JSON.stringify(data.user));
            window.location.href = 'index.html';
        } else {
            const error = await res.json();
            alert("Login Failed: " + (error.detail || "Invalid credentials"));
        }
    } catch (err) {
        console.error("Login Exception:", err);
        alert("Connectivity Error: Could not reach the server.");
    } finally {
        btn.innerText = origText;
        btn.disabled = false;
    }
}

async function handleSignup(e) {
    if (e) e.preventDefault();
    const fullname = document.getElementById('fullname').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = e.target.querySelector('button');
    const origText = btn.innerText;

    btn.innerText = "⏳ Registering Profile...";
    btn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/api/auth/signup`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({fullname, email, password})
        });
        
        if (res.ok) {
            localStorage.setItem('auth', 'true');
            localStorage.setItem('user', JSON.stringify({fullname, email}));
            window.location.href = 'index.html';
        } else {
            const error = await res.json();
            alert("Signup Rejected: " + (error.detail || "Unable to create account"));
        }
    } catch (err) {
        console.error("Signup Exception:", err);
        alert("Connectivity Error: Could not synchronize with the system.");
    } finally {
        btn.innerText = origText;
        btn.disabled = false;
    }
}

function handleLogout() {
    localStorage.removeItem('auth');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function requireAuth() {
    if (localStorage.getItem('auth') !== 'true') {
        window.location.href = 'login.html';
    }
}

function toggleAuth() {
    if (localStorage.getItem('auth') === 'true') {
        handleLogout();
    } else {
        window.location.href = 'login.html';
    }
}

function showProfile() {
    if (localStorage.getItem('auth') === 'true') {
        window.location.href = 'profile.html';
    } else {
        window.location.href = 'login.html';
    }
}

function showCart() {
    alert("Procurement cart is empty.");
}

// On Page Load: Update Navigation State based on Auth
window.addEventListener('DOMContentLoaded', () => {
    const authBtn = document.getElementById('authBtn');
    if (authBtn) {
        if (localStorage.getItem('auth') === 'true') {
            authBtn.innerText = 'Logout';
            authBtn.style.background = 'transparent';
            authBtn.style.border = '1px solid var(--text-muted)';
            authBtn.style.color = 'var(--text-muted)';
        } else {
            authBtn.innerText = 'Sign in';
        }
    }

    // Handle incoming search query from header (supports both 'search' and 'q' for robustness)
    const params = new URLSearchParams(window.location.search);
    const searchQuery = params.get('search') || params.get('q');
    const analyzerSearchInput = document.getElementById('medSearch');
    
    if (searchQuery && analyzerSearchInput) {
        analyzerSearchInput.value = searchQuery;
        runAnalysis();
    }

    // Handle autofocus for AI Chatbot
    if (params.get('autofocus') === 'true') {
        const headerInput = document.getElementById('headerSearch');
        if (headerInput) {
            headerInput.focus();
            // Optional: clear any previous value
            headerInput.value = '';
        }
    }
    // Set active nav link
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
