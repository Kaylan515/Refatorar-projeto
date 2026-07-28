# ============================================================
# controllers/movimentacao_controller.py
# ============================================================
# Entradas e saídas de estoque.
# Qualquer usuário logado pode registrar movimentações.
# Somente admins podem ver o histórico completo de todos
# os produtos — operadores veem apenas suas próprias.
# ============================================================

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movimentacao import Movimentacao, Tipo_de_movimentacao as TipoMovimentacao
from app.models.produto import Produto, ProdutoVariacao
from app.auth import get_usuario_logado, get_admin

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])

templates = Jinja2Templates(directory="app/templates")


# ============================================================
# HISTÓRICO GERAL — somente admin
# ============================================================

@router.get("/")
def listar_movimentacoes(
    request: Request,
    produto_id: int = 0,     # filtra por produto específico
    tipo: str = "",          # "entrada" ou "saida"
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    """
    Exibe o histórico completo de movimentações com filtros
    por produto e tipo. Acessível apenas por admins.
    """
    query = db.query(Movimentacao).order_by(Movimentacao.criando_em.desc())

    if produto_id:
        query = query.filter(Movimentacao.produto_id == produto_id)

    if tipo in ("entrada", "saida", "cancelamento", "ajuste"):
        query = query.filter(Movimentacao.tipo == tipo)

    movimentacoes = query.limit(200).all()  # limita para não sobrecarregar
    produtos      = db.query(Produto).filter(Produto.ativo == True).all()

    return templates.TemplateResponse(
        request,
        "movimentacoes/index.html",
        {
            "request":        request,
            "usuario":        admin,
            "movimentacoes":  movimentacoes,
            "produtos":       produtos,
            "produto_id":     produto_id,
            "tipo":           tipo,
        }
    )


# ============================================================
# REGISTRAR MOVIMENTAÇÃO
# ============================================================

@router.get("/nova")
def form_nova_movimentacao(
    request: Request,
    produto_id: int = 0,   # pré-seleciona o produto se vier da página de detalhe
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    """
    Exibe o formulário de registro de movimentação.
    Pode receber produto_id via query string para
    pré-selecionar o produto direto da página de detalhe.
    """
    produtos = db.query(Produto).filter(Produto.ativo == True).all()

    return templates.TemplateResponse(
        request,
        "movimentacoes/form.html",
        {
            "request":    request,
            "usuario":    usuario,
            "produtos":   produtos,
            "produto_id": produto_id,
            "tipos":      TipoMovimentacao,  # passa o enum para o template
        }
    )


@router.post("/nova")
def registrar_movimentacao(
    request: Request,
    produto_id: int           = Form(...),
    produto_variacao_id: int  = Form(0),
    tipo: str                 = Form(...),
    quantidade: int           = Form(...),
    preco_unitario: float     = Form(...),
    observacao: str           = Form(""),
    db: Session               = Depends(get_db),
    usuario                   = Depends(get_usuario_logado)
):
    """
    Registra a movimentação de uma variação de produto e atualiza
    o estoque da variação em uma única transação.
    """
    produtos = db.query(Produto).filter(Produto.ativo == True).all()

    if tipo not in (TipoMovimentacao.ENTRADA, TipoMovimentacao.SAIDA):
        return templates.TemplateResponse(
            request,
            "movimentacoes/form.html",
            {
                "request":    request,
                "usuario":    usuario,
                "produtos":   produtos,
                "produto_id": produto_id,
                "tipos":      TipoMovimentacao,
                "erro":       "Tipo de movimentação inválido.",
            },
            status_code=400
        )

    if quantidade <= 0:
        return templates.TemplateResponse(
            request,
            "movimentacoes/form.html",
            {
                "request":    request,
                "usuario":    usuario,
                "produtos":   produtos,
                "produto_id": produto_id,
                "tipos":      TipoMovimentacao,
                "erro":       "A quantidade deve ser maior que zero.",
            },
            status_code=400
        )

    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        return RedirectResponse(url="/movimentacoes/nova", status_code=302)

    variacao = None
    if produto_variacao_id:
        variacao = db.query(ProdutoVariacao).filter(
            ProdutoVariacao.id == produto_variacao_id,
            ProdutoVariacao.produto_id == produto_id
        ).with_for_update().first()

        if not variacao:
            return templates.TemplateResponse(
                request,
                "movimentacoes/form.html",
                {
                    "request":    request,
                    "usuario":    usuario,
                    "produtos":   produtos,
                    "produto_id": produto_id,
                    "tipos":      TipoMovimentacao,
                    "erro":       "Variação de produto inválida.",
                },
                status_code=400
            )
    else:
        variacao = next((v for v in produto.variacoes if v.ativo), None)
        if not variacao:
            return templates.TemplateResponse(
                request,
                "movimentacoes/form.html",
                {
                    "request":    request,
                    "usuario":    usuario,
                    "produtos":   produtos,
                    "produto_id": produto_id,
                    "tipos":      TipoMovimentacao,
                    "erro":       "Nenhuma variação ativa disponível.",
                },
                status_code=400
            )

    if tipo == TipoMovimentacao.SAIDA and quantidade > variacao.estoque_atual:
        return templates.TemplateResponse(
            request,
            "movimentacoes/form.html",
            {
                "request":    request,
                "usuario":    usuario,
                "produtos":   produtos,
                "produto_id": produto_id,
                "tipos":      TipoMovimentacao,
                "erro": (
                    f"Estoque insuficiente. "
                    f"Disponível: {variacao.estoque_atual} unidade(s)."
                ),
            },
            status_code=400
        )

    if tipo == TipoMovimentacao.ENTRADA:
        variacao.estoque_atual += quantidade
    else:
        variacao.estoque_atual -= quantidade

    movimentacao = Movimentacao(
        tipo                   = tipo,
        quantidade             = quantidade,
        preco_unitario         = preco_unitario,
        observacao             = observacao or None,
        produto_id             = produto_id,
        produto_variacao_id    = variacao.id,
        usuario_id             = usuario.get("id"),
    )

    db.add(movimentacao)
    db.commit()

    return RedirectResponse(
        url=f"/produtos/{produto_id}?movimentacao=ok",
        status_code=302
    )


# ============================================================
# HISTÓRICO POR PRODUTO — acessível por qualquer logado
# ============================================================

@router.get("/produto/{produto_id}")
def historico_produto(
    produto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    """
    Exibe o histórico de movimentações de um produto específico
    com o resumo de entradas, saídas e saldo.
    """
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        return RedirectResponse(url="/produtos", status_code=302)

    movimentacoes = (
        db.query(Movimentacao)
        .filter(Movimentacao.produto_id == produto_id)
        .order_by(Movimentacao.criando_em.desc())
        .all()
    )

    # Resumo calculado em Python a partir do histórico
    total_entradas = sum(
        m.quantidade for m in movimentacoes
        if m.tipo == TipoMovimentacao.ENTRADA
    )
    total_saidas = sum(
        m.quantidade for m in movimentacoes
        if m.tipo == TipoMovimentacao.SAIDA
    )

    return templates.TemplateResponse(
        request,
        "movimentacoes/historico.html",
        {
            "request":        request,
            "usuario":        usuario,
            "produto":        produto,
            "movimentacoes":  movimentacoes,
            "total_entradas": total_entradas,
            "total_saidas":   total_saidas,
        }
    )