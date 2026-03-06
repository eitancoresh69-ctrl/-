const App = {
    currentSport: 'soccer',
    apiHost: 'http://127.0.0.1:8000',

    init() {
        console.log("מערכת SportIQ מאותחלת...");
        this.fetchUpcomingGames();
    },

    switchSport(sport) {
        this.currentSport = sport;
        document.querySelectorAll('.controls button').forEach(b => b.classList.remove('active'));
        document.getElementById(`btn-${sport}`).classList.add('active');
        this.fetchUpcomingGames();
    },

    async fetchUpcomingGames() {
        const list = document.getElementById('games-list');
        list.innerHTML = '<div class="loader">טוען נתונים...</div>';
        
        try {
            // קריאה לשרת הפייתון המקומי שלנו
            const res = await fetch(`${this.apiHost}/api/games/${this.currentSport}/upcoming`);
            const data = await res.json();
            this.renderGames(data.events || []);
        } catch (err) {
            list.innerHTML = '<div class="error">שגיאה בחיבור לשרת המקומי</div>';
        }
    },

    renderGames(games) {
        const list = document.getElementById('games-list');
        if (games.length === 0) {
            list.innerHTML = '<div class="empty">אין משחקים רלוונטיים ב-5 הימים הקרובים.</div>';
            return;
        }

        list.innerHTML = games.map(g => `
            <div class="game-card" onclick="App.loadAnalysis('${g.id}')">
                <div class="league-name">${g.league}</div>
                <div class="teams">${g.homeTeam} - ${g.awayTeam}</div>
                <div class="game-time">${g.date}</div>
            </div>
        `).join('');
    },

    // חישוב מבוסס קריטריון קלי
    calculateKelly(prob, odds) {
        const p = prob / 100;
        const b = parseFloat(odds) - 1;
        const k = (b * p - (1 - p)) / b;
        return Math.max(0, Math.min(k * 100, 25)).toFixed(1);
    },

    loadAnalysis(gameId) {
        const board = document.getElementById('analysis-content');
        board.innerHTML = `
            <div class="ai-box">
                <h3>ניתוח הסתברויות וערך (Value)</h3>
                <p>מחשב נתוני עומק למשחק...</p>
                </div>
        `;
        // כאן תכנס הקריאה לראוט /api/analysis/{game_id}
    }
};

window.onload = () => App.init();
