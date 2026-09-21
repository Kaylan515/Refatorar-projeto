document.addEventListener('DOMContentLoaded', () => {
    // Efeito de Spotlight interativo seguindo o mouse
    const spotlight = document.getElementById('spotlight');

    if (spotlight) {
        window.addEventListener('mousemove', (e) => {
            const x = e.clientX;
            const y = e.clientY;
            spotlight.style.left = `${x}px`;
            spotlight.style.top = `${y}px`;
        });
    }
});