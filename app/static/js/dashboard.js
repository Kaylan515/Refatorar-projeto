/**
 * ==========================================================================
 * DASHBOARD SCRIPT — AAPM SENAI
 * Gestão de interatividade, spotlight e comportamentos dinâmicos do painel.
 * ==========================================================================
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        setupSpotlightEffect();
        setupInteractiveRows();
    });

    /**
     * Efeito de luz interativa do cursor (Spotlight SaaS)
     */
    function setupSpotlightEffect() {
        const spotlight = document.getElementById('spotlight');
        if (!spotlight) return;

        let mouseX = 0;
        let mouseY = 0;
        let currentX = 0;
        let currentY = 0;

        window.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        function renderSpotlight() {
            currentX += (mouseX - currentX) * 0.1;
            currentY += (mouseY - currentY) * 0.1;

            spotlight.style.transform = `translate(${currentX}px, ${currentY}px) translate(-50%, -50%)`;
            requestAnimationFrame(renderSpotlight);
        }

        renderSpotlight();
    }

    /**
     * Torna as linhas das tabelas interativas e clicáveis com feedback visual
     */
    function setupInteractiveRows() {
        const rows = document.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const link = row.querySelector('.td-name');
            if (link) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', (e) => {
                    if (e.target.tagName.toLowerCase() === 'a') return;
                    window.location.href = link.href;
                });
            }
        });
    }
})();