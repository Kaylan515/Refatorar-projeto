from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.categoria import Categoria

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    estoque_atual = Column(Integer, nullable=False, default=0)
    preco = Column(Integer, nullable=False, default=0.0)
    ativo = Column(Boolean, default=True)

    #caminho da imagem do produto, pode ser um URL ou caminho local
    imagem_path = Column(String(255), nullable=True)

    #Relacionamento com categoria
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)
    categoria = relationship("Categoria", back_populates="produtos")


    #Método
    @property
    def imagem_url(self):
        if self.imagem_path:
            return f"/static/{self.imagem_path}"
        else:
            return "/static/imagens/default.png"  # Caminho para imagem padrão caso não haja imagem específica
        

    