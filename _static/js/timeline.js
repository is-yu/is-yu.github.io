/* AI Breakthroughs — D3.js Interactive Timeline */

(function() {
    const container = document.getElementById('timeline-viz');
    if (!container) return;

    const BASE_URL = '/ai-breakthroughs';
    const margin = { top: 30, right: 30, bottom: 40, left: 30 };

    function render() {
        container.innerHTML = '';
        const width = container.clientWidth;
        const height = 320;
        const innerW = width - margin.left - margin.right;
        const innerH = height - margin.top - margin.bottom;

        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        d3.json(`${BASE_URL}/static/data/timeline.json`).then(function(data) {
            if (!data || !data.events || data.events.length === 0) {
                g.append('text')
                    .attr('x', innerW / 2)
                    .attr('y', innerH / 2)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#8888a0')
                    .text('No timeline data available.');
                return;
            }

            const yearMin = d3.min(data.eras, d => d.start);
            const yearMax = 2027;

            const x = d3.scaleLinear()
                .domain([yearMin, yearMax])
                .range([0, innerW]);

            // Draw era bands
            data.eras.forEach(function(era) {
                g.append('rect')
                    .attr('x', x(era.start))
                    .attr('y', 0)
                    .attr('width', x(era.end) - x(era.start))
                    .attr('height', innerH)
                    .attr('fill', era.color)
                    .attr('opacity', 0.08);

                // Era label (only if wide enough)
                const eraWidth = x(era.end) - x(era.start);
                if (eraWidth > 60) {
                    g.append('text')
                        .attr('x', x(era.start) + eraWidth / 2)
                        .attr('y', innerH + 28)
                        .attr('text-anchor', 'middle')
                        .attr('fill', era.color)
                        .attr('font-size', '9px')
                        .attr('opacity', 0.7)
                        .text(era.name.length > 15 ? era.name.slice(0, 15) + '...' : era.name);
                }
            });

            // X axis
            const xAxis = d3.axisBottom(x)
                .tickFormat(d3.format('d'))
                .ticks(Math.min(Math.floor(innerW / 80), 12));

            g.append('g')
                .attr('transform', `translate(0,${innerH})`)
                .call(xAxis)
                .selectAll('text')
                .attr('fill', '#8888a0')
                .attr('font-size', '11px');

            g.selectAll('.domain, .tick line')
                .attr('stroke', '#2a2a3a');

            // Significance to radius
            const sizeScale = {
                'paradigm-shift': 10,
                'major': 7,
                'significant': 5,
                'incremental': 3,
            };

            // Separate breakthroughs and questions for y positioning
            const breakthroughs = data.events.filter(e => e.type === 'breakthrough');
            const questions = data.events.filter(e => e.type !== 'breakthrough');

            // Position breakthroughs in top half, questions in bottom half
            const bY = innerH * 0.3;
            const qY = innerH * 0.7;

            // Tooltip
            const tooltip = d3.select(container)
                .append('div')
                .style('position', 'absolute')
                .style('background', '#1a1a25')
                .style('border', '1px solid #2a2a3a')
                .style('border-radius', '6px')
                .style('padding', '8px 12px')
                .style('font-size', '12px')
                .style('color', '#e0e0e8')
                .style('pointer-events', 'none')
                .style('opacity', 0)
                .style('z-index', 10)
                .style('max-width', '250px');

            // Draw breakthroughs (circles)
            g.selectAll('.bt-dot')
                .data(breakthroughs)
                .enter()
                .append('circle')
                .attr('cx', d => x(d.year))
                .attr('cy', (d, i) => bY + (i % 3 - 1) * 25)
                .attr('r', d => sizeScale[d.significance] || 5)
                .attr('fill', d => {
                    const colors = {
                        'paradigm-shift': '#9b59b6',
                        'major': '#e74c3c',
                        'significant': '#3498db',
                        'incremental': '#7f8c8d',
                    };
                    return colors[d.significance] || '#6c8cff';
                })
                .attr('opacity', 0.85)
                .attr('cursor', 'pointer')
                .on('mouseover', function(event, d) {
                    d3.select(this).attr('opacity', 1).attr('r', (sizeScale[d.significance] || 5) + 3);
                    tooltip.style('opacity', 1)
                        .html(`<strong>${d.title}</strong><br>${d.date}<br><span style="color:#8888a0">${d.significance}</span>`);
                })
                .on('mousemove', function(event) {
                    const rect = container.getBoundingClientRect();
                    tooltip.style('left', (event.clientX - rect.left + 12) + 'px')
                           .style('top', (event.clientY - rect.top - 10) + 'px');
                })
                .on('mouseout', function(event, d) {
                    d3.select(this).attr('opacity', 0.85).attr('r', sizeScale[d.significance] || 5);
                    tooltip.style('opacity', 0);
                })
                .on('click', function(event, d) {
                    window.location.href = d.url;
                });

            // Draw questions (diamonds)
            g.selectAll('.q-dot')
                .data(questions)
                .enter()
                .append('path')
                .attr('d', d3.symbol().type(d3.symbolDiamond).size(80))
                .attr('transform', (d, i) => `translate(${x(d.year)},${qY + (i % 3 - 1) * 20})`)
                .attr('fill', d => d.status === 'OPEN' ? '#e74c3c' : d.status === 'PARTIALLY_ANSWERED' ? '#f39c12' : '#2ecc71')
                .attr('opacity', 0.85)
                .attr('cursor', 'pointer')
                .on('mouseover', function(event, d) {
                    d3.select(this).attr('opacity', 1);
                    tooltip.style('opacity', 1)
                        .html(`<strong>${d.title}</strong><br>${d.date}<br><span style="color:#8888a0">${d.status}</span>`);
                })
                .on('mousemove', function(event) {
                    const rect = container.getBoundingClientRect();
                    tooltip.style('left', (event.clientX - rect.left + 12) + 'px')
                           .style('top', (event.clientY - rect.top - 10) + 'px');
                })
                .on('mouseout', function() {
                    d3.select(this).attr('opacity', 0.85);
                    tooltip.style('opacity', 0);
                })
                .on('click', function(event, d) {
                    window.location.href = d.url;
                });

            // Legend
            const legend = svg.append('g')
                .attr('transform', `translate(${margin.left + 10}, 12)`);

            const legendItems = [
                { label: 'Breakthrough', shape: 'circle', color: '#6c8cff' },
                { label: 'Answered', shape: 'diamond', color: '#2ecc71' },
                { label: 'Open', shape: 'diamond', color: '#e74c3c' },
            ];

            legendItems.forEach(function(item, i) {
                const lg = legend.append('g')
                    .attr('transform', `translate(${i * 110}, 0)`);

                if (item.shape === 'circle') {
                    lg.append('circle').attr('cx', 6).attr('cy', 0).attr('r', 5).attr('fill', item.color);
                } else {
                    lg.append('path')
                        .attr('d', d3.symbol().type(d3.symbolDiamond).size(50))
                        .attr('transform', 'translate(6,0)')
                        .attr('fill', item.color);
                }
                lg.append('text')
                    .attr('x', 16).attr('y', 4)
                    .attr('fill', '#8888a0')
                    .attr('font-size', '11px')
                    .text(item.label);
            });
        });
    }

    render();
    window.addEventListener('resize', render);
})();
