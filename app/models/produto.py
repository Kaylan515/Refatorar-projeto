from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.categoria import Categoria

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    ativo = Column(Boolean, default=True)

    # caminho da imagem do produto, pode ser um URL ou caminho local
    imagem_path = Column(String(255), nullable=True)

    # Relacionamento com categoria
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)
    categoria = relationship("Categoria", back_populates="produtos")

    # Relacionamento com variações
    variacoes = relationship(
        "ProdutoVariacao",
        back_populates="produto",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @property
    def imagem_url(self):
        if self.imagem_path:
            return f"/static/{self.imagem_path}"
        else:
            return "/static/imagens/default.png"

    @property
    def estoque_total(self) -> int:
        return sum(variacao.estoque_atual for variacao in self.variacoes if variacao.ativo)

    @property
    def preco_minimo(self) -> float:
        valores = [variacao.preco for variacao in self.variacoes if variacao.ativo]
        return min(valores) if valores else 0.0

    @property
    def preco_maximo(self) -> float:
        valores = [variacao.preco for variacao in self.variacoes if variacao.ativo]
        return max(valores) if valores else 0.0


class ProdutoVariacao(Base):
    __tablename__ = "produto_variacoes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False)
    cor = Column(String(50), nullable=True)
    tamanho = Column(String(50), nullable=True)
    preco = Column(Float, nullable=False, default=0.0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True)

    produto = relationship("Produto", back_populates="variacoes")
    movimentacoes = relationship("Movimentacao", back_populates="variacao")
    itens_venda = relationship("ItemVenda", back_populates="variacao")

    @property
    def descricao(self) -> str:
        partes = [parte for parte in (self.cor, self.tamanho) if parte]
        return " / ".join(partes)

    @property
    def nome_completo(self) -> str:
        descricao = self.descricao
        if descricao:
            return f"{self.produto.nome} - {descricao}"
        return self.produto.nome


    