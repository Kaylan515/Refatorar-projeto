(() => {
    function mountShell() {
        const body = document.body;
        if (body.classList.contains('auth-page') || body.querySelector('.layout, .page-wrapper, .topbar, .cupom')) return;

        const shell = document.createElement('div');
        shell.className = 'app-shell';
        shell.innerHTML = '<header class="app-shell-header"><a class="app-shell-brand" href="/">AAPM <span>•</span> SENAI</a><nav class="app-shell-nav" aria-label="Navegação principal"><a href="/">Dashboard</a><a href="/produtos">Produtos</a><a href="/armarios">Armários</a><a href="/pdv">PDV</a></nav></header><main class="app-content"></main><footer class="app-shell-footer"><span><strong>AAPM SENAI</strong> · Gestão acadêmica e operacional</span><a href="/">Ir ao dashboard</a></footer>';

        const content = shell.querySelector('.app-content');
        [...body.childNodes].forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'SCRIPT') return;
            if (node.nodeType === Node.TEXT_NODE && !node.textContent.trim()) return;
            content.append(node);
        });
        body.prepend(shell);
        shell.querySelectorAll('.app-shell-nav a').forEach((link) => {
            if (link.pathname === window.location.pathname) link.setAttribute('aria-current', 'page');
        });
    }

    function openConfirmation(form, message) {
        const dialog = document.createElement('div');
        dialog.className = 'app-confirm-backdrop';
        dialog.innerHTML = '<section class="app-confirm-dialog" role="alertdialog" aria-modal="true"><h2>Confirmar ação</h2><p></p><div class="app-confirm-actions"><button type="button" class="app-confirm-cancel">Cancelar</button><button type="button" class="app-confirm-accept">Confirmar</button></div></section>';
        dialog.querySelector('p').textContent = message;
        dialog.querySelector('.app-confirm-cancel').addEventListener('click', () => dialog.remove());
        dialog.querySelector('.app-confirm-accept').addEventListener('click', () => {
            form.classList.add('is-submitting');
            dialog.remove();
            form.submit();
        });
        document.body.append(dialog);
        dialog.querySelector('.app-confirm-cancel').focus();
    }

    document.addEventListener('DOMContentLoaded', () => {
        mountShell();
        document.addEventListener('click', (event) => {
            const target = event.target.closest('button, .btn-primary, .btn-secondary');
            if (!target || target.disabled) return;

            const ripple = document.createElement('span');
            ripple.className = 'ui-ripple';
            const bounds = target.getBoundingClientRect();
            ripple.style.left = `${event.clientX - bounds.left}px`;
            ripple.style.top = `${event.clientY - bounds.top}px`;
            target.append(ripple);
            ripple.addEventListener('animationend', () => ripple.remove());
        });
        // Melhora a UX da paginação evitando cliques duplos
        document.querySelectorAll('.pagination a').forEach((link) => {
            link.addEventListener('click', () => {
                link.style.pointerEvents = 'none';
                link.style.opacity = '.7';
                link.setAttribute('aria-busy', 'true');
            });
        });

        // Confirmação inteligente para formulários POST (exceto rotas de auth e pdv)
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

        document.addEventListener('submit', (event) => {
            const form = event.target;
            if (!(form instanceof HTMLFormElement) || form.method.toLowerCase() !== 'post') return;
            const action = form.getAttribute('action') || '';
            if (action.startsWith('/auth/') || action === '/pdv/finalizar') return;

            event.preventDefault();
            event.stopImmediatePropagation();
            const label = event.submitter?.textContent?.trim() || 'confirmar esta ação';
            openConfirmation(form, form.dataset.confirm || `Deseja ${label.toLowerCase()}?`);
        }, true);
    });
})();
