# ============================================================
# main.py — Ponto de entrada da aplicação
# ============================================================

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.controllers import auth_controller
from app.auth import get_usuario_opcional  # ← troca aqui
from app.controllers import usuario_controller  # ← adicionar
from app.controllers import produto_controller  # ← adicionar
from app.controllers import categoria_controller
from app.controllers import movimentacao_controller
from app.controllers import armario_controller  # ← adicionar

from app.controllers import cliente_controller, pdv_controller
from app.database import engine
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.movimentacao import Movimentacao
from app.models.armario import Armario, StatusArmario
from sqlalchemy.orm import Session

app = FastAPI(title="Sistema de Estoque")

#Configura o FastAPI para servir arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configura o Jinja2 para renderizar os templates HTML
templates = Jinja2Templates(directory="app/templates")
def _dados_dashboard() -> dict:
    """Monta os indicadores exibidos no painel principal."""
    with Session(engine) as db:
        total_produtos = db.query(Produto).filter(Produto.ativo == True).count()
        total_categorias = db.query(Categoria).filter(Categoria.ativo == True).count()
        estoque_baixo = (
            db.query(Produto)
            .filter(Produto.ativo == True, Produto.estoque_atual <= 5)
            .order_by(Produto.estoque_atual, Produto.nome)
            .all()
        )
        movimentacoes_recentes = (
            db.query(Movimentacao)
            .order_by(Movimentacao.criado_em.desc())
            .limit(5)
            .all()
        )
        total_armarios = db.query(Armario).filter(Armario.ativo == True).count()
        armarios_disponiveis = (
            db.query(Armario)
            .filter(Armario.ativo == True, Armario.status == StatusArmario.DISPONIVEL)
            .count()
        )
        armarios_alugados = (
            db.query(Armario)
            .filter(Armario.ativo == True, Armario.status == StatusArmario.ALUGADO)
            .count()
        )

        return {
            "total_produtos": total_produtos,
            "total_categorias": total_categorias,
            "estoque_baixo": estoque_baixo,
            "movimentacoes_recentes": movimentacoes_recentes,
            "total_armarios": total_armarios,
            "armarios_disponiveis": armarios_disponiveis,
            "armarios_alugados": armarios_alugados,
        }

# Inclui os routers dos controladores
app.include_router(auth_controller.router)
app.include_router(cliente_controller.router)
app.include_router(pdv_controller.router)
# Inclui o router do controlador de usuários (admin)
app.include_router(usuario_controller.router)  # ← adicionar
app.include_router(produto_controller.router)  # ← adicionar
app.include_router(categoria_controller.router)
app.include_router(movimentacao_controller.router)
app.include_router(armario_controller.router)   # ← adicionar


#Rodar o código: python -m uvicorn app.main:app --reload


@app.get("/")
def dashboard(
    request: Request,
    usuario = Depends(get_usuario_opcional)  # ← não lança erro se não logado
):
    """
    Se o usuário estiver logado, mostra o dashboard.
    Se não estiver, renderiza uma página de boas-vindas
    com links para login e cadastro — sem nenhum erro.
    """

    if usuario is None:
        # Não logado — exibe página pública de boas-vindas
        return templates.TemplateResponse(
            request,
            "welcome.html",
            {"request": request}
        )

    # Logado — exibe o dashboard com os dados do usuário
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request, "usuario": usuario, **_dados_dashboard()}
    )
    
