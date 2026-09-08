(() => {
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.pagination a').forEach((link) => {
            link.addEventListener('click', () => {
                link.style.pointerEvents = 'none';
                link.style.opacity = '.7';
                link.setAttribute('aria-busy', 'true');
            });
        });

        document.querySelectorAll('form[method="post"]').forEach((form) => {
            const action = form.getAttribute('action') || '';
            const possuiConfirmacaoPropria = form.hasAttribute('onsubmit');
            const rotaExcluida = action.startsWith('/auth/') || action === '/pdv/finalizar';

            if (possuiConfirmacaoPropria || rotaExcluida) return;

            form.addEventListener('submit', (evento) => {
                const botao = evento.submitter;
                const textoAcao = botao?.textContent?.trim() || 'confirmar esta ação';
                if (!window.confirm(`Deseja ${textoAcao.toLowerCase()}?`)) {
                    evento.preventDefault();
                }
            });
        });
    });
    return;

    const storageKey = 'aapm-theme';
    const root = document.documentElement;

    const aplicarTema = (tema) => {
        root.dataset.theme = tema;
        localStorage.setItem(storageKey, tema);
        const botao = document.querySelector('.theme-toggle');
        if (botao) {
            const claro = tema === 'light';
            botao.setAttribute('aria-pressed', String(claro));
            botao.innerHTML = claro ? '☀️ Tema claro' : '🌙 Tema escuro';
        }
    };

    const temaSalvo = localStorage.getItem(storageKey);
    aplicarTema(temaSalvo || 'dark');

    document.addEventListener('DOMContentLoaded', () => {
        const botao = document.createElement('button');
        botao.type = 'button';
        botao.className = 'theme-toggle';
        botao.setAttribute('aria-label', 'Alternar tema claro e escuro');
        botao.addEventListener('click', () => aplicarTema(root.dataset.theme === 'dark' ? 'light' : 'dark'));
        document.body.append(botao);
        aplicarTema(root.dataset.theme);

        document.querySelectorAll('.pagination a').forEach((link) => {
            link.addEventListener('click', () => {
                link.style.pointerEvents = 'none';
                link.style.opacity = '.7';
                link.setAttribute('aria-busy', 'true');
            });
        });
    });
})();
