class ProductBuyModel:
    def __init__(self, product_id: str, numero_cartao: str, data_expiracao: str, cvv: str):
        self.product_id = product_id
        self.numero_cartao = numero_cartao
        self.data_expiracao = data_expiracao
        self.cvv = cvv

    def __repr__(self):
        return f"<Compra {self.product_id} - Cartão: {self.numero_cartao[-4:]}*>"