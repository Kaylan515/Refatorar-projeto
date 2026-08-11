import os
import shutil
import uuid
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.produto import Produto, ProdutoVariacao
from app.models.categoria import Categoria
from app.auth import get_usuario_logado, get_admin

# Criação do router
router = APIRouter(prefix="/produtos", tags=["Produtos"])

# Configuração de templates
templates = Jinja2Templates(directory="app/templates")

# Pasta de uploads
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def _salvar_imagem(imagem: UploadFile):
    if imagem:
        filename = f"{uuid.uuid4()}_{imagem.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
        return f"/static/uploads/{filename}"
    return None

def _remover_imagem(path: str):
    if path:
        filepath = path.replace("/static/", "app/static/")
        if os.path.exists(filepath):
            os.remove(filepath)

def _produto_existe(db: Session, nome: str, ignorar_id: int = None) -> bool:
    query = db.query(Produto).filter(Produto.nome.ilike(nome))
    if ignorar_id:
        query = query.filter(Produto.id != ignorar_id)
    return query.first() is not None

def _categorias_ativas(db: Session):
    return db.query(Categoria).filter(Categoria.ativo == True).all()

# ============================================================
# CADASTRO
# ============================================================

@router.post("/novo")
async def criar_produto(
    request: Request,
    nome: str          = Form(...),
    preco: float       = Form(...),
    estoque_atual: int = Form(...),
    cor: str           = Form(""),
    tamanho: str       = Form(""),
    categoria_id: int  = Form(...),
    imagem: UploadFile = File(None),
    db: Session        = Depends(get_db),
    admin              = Depends(get_admin)
):
    categorias = _categorias_ativas(db)

    if _produto_existe(db, nome):
        return templates.TemplateResponse(
            request,
            "produtos/form.html",
            {
                "request": request,
                "usuario": admin,
                "categorias": categorias,
                "erro": "Já existe um produto com este nome.",
            },
            status_code=400
        )

    if estoque_atual < 0:
        return templates.TemplateResponse(
            request,
            "produtos/form.html",
            {
                "request": request,
                "usuario": admin,
                "categorias": categorias,
                "erro": "Estoque não pode ser negativo.",
            },
            status_code=400
        )

    imagem_path = _salvar_imagem(imagem)

    produto = Produto(
        nome=nome,
        categoria_id=categoria_id,
        imagem_path=imagem_path,
    )
    db.add(produto)
    db.flush()

    variacao = ProdutoVariacao(
        produto_id=produto.id,
        cor=cor or None,
        tamanho=tamanho or None,
        preco=preco,
        estoque_atual=estoque_atual
    )
    db.add(variacao)
    db.commit()

    return RedirectResponse(url="/produtos?criado=ok", status_code=302)
