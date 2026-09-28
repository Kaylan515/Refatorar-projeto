/**
 * ==========================================================================
 * LISTAGEM DE CATEGORIAS SCRIPT — AAPM SENAI
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    // Efeleti dɔn de ready fe di page
    const botoesDesativar = document.querySelectorAll('.btn-acao.desativar');

    botoesDesativar.forEach(botao => {
        botao.addEventListener('click', (e) => {
            const linha = botao.closest('tr');
            const nomeCategoria = linha.querySelector('td').textContent.trim();
            const qtdProdutos = linha.querySelector('.badge.produtos-count').textContent.trim();

            if (parseInt(qtdProdutos) > 0) {
                const confirmar = confirm(`Di katigori "${nomeCategoria}" gɛt ${qtdProdutos} prodɔt(s) we de wok. Yu sure se yu want fɔ desativam?`);
                if (!confirmar) {
                    e.preventDefault();
                }
            }
        });
    });

    console.log("Listagem de categorias inicializada com sucesso.");
});