/* AI Breakthroughs — Client-side search */

(function() {
    const input = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');
    if (!input || !resultsContainer) return;

    const BASE_URL = '/ai-breakthroughs';
    let docs = [];

    // Load search index
    fetch(`${BASE_URL}/static/data/search-index.json`)
        .then(r => r.json())
        .then(data => { docs = data.docs || []; })
        .catch(() => {
            resultsContainer.innerHTML = '<p style="color: var(--color-text-muted);">Failed to load search index.</p>';
        });

    input.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();

        if (query.length < 2) {
            resultsContainer.innerHTML = '<p style="color: var(--color-text-muted); text-align: center; padding: 32px;">Start typing to search across all questions and breakthroughs.</p>';
            return;
        }

        const terms = query.split(/\s+/);
        const results = docs
            .map(function(doc) {
                const text = `${doc.title} ${doc.body || ''} ${doc.tags || ''} ${doc.authors || ''}`.toLowerCase();
                let score = 0;
                terms.forEach(function(term) {
                    if (text.includes(term)) {
                        score += 1;
                        if (doc.title.toLowerCase().includes(term)) score += 2;
                    }
                });
                return { doc: doc, score: score };
            })
            .filter(r => r.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 20);

        if (results.length === 0) {
            resultsContainer.innerHTML = '<p style="color: var(--color-text-muted); text-align: center; padding: 32px;">No results found.</p>';
            return;
        }

        const typeLabels = {
            question: 'Question',
            breakthrough: 'Breakthrough',
            progress: 'Progress',
        };

        resultsContainer.innerHTML = results.map(function(r) {
            const d = r.doc;
            const snippet = (d.body || '').slice(0, 200);
            return `
                <div class="search-result">
                    <div class="search-result-type">${typeLabels[d.type] || d.type}</div>
                    <div class="search-result-title"><a href="${d.url}">${d.title}</a></div>
                    <div class="search-result-body">${snippet}...</div>
                </div>
            `;
        }).join('');
    });
})();
