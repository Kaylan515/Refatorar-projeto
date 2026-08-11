from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    imagem_path = Column(String, nullable=True)
    ativo = Column(Boolean, default=True)

    variacoes = relationship("ProdutoVariacao", back_populates="produto")


class ProdutoVariacao(Base):
    __tablename__ = "produto_variacoes"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    cor = Column(String, nullable=True)
    tamanho = Column(String, nullable=True)
    preco = Column(Float, nullable=False)
    estoque_atual = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)

    produto = relationship("Produto", back_populates="variacoes")
