/* AI Breakthroughs — Client-side filtering */

(function() {
    const filterBar = document.getElementById('filters');
    const grid = document.getElementById('questions-grid');
    if (!filterBar || !grid) return;

    const cards = grid.querySelectorAll('.card');
    const buttons = filterBar.querySelectorAll('.filter-btn');

    buttons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;

            cards.forEach(function(card) {
                if (filter === 'all' || card.dataset.status === filter) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
})();
