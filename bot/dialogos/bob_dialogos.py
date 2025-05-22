from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes, CardAction, ActionTypes
import aiohttp
import json
from urllib.parse import quote

class BobDialogo(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        super(BobDialogo, self).__init__()
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.api_url = "http://localhost:8080/product"
        self.api_search_url = "http://localhost:8080/product/search"

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self.enviar_boas_vindas(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        texto = turn_context.activity.text.strip().lower()

        if texto in ["ver todos os produtos", "todos", "listar produtos"]:
            await self.mostrar_produtos(turn_context)
            return

        if texto in ["consultar produto especifico", "produto especifico"]:
            await turn_context.send_activity("Digite o nome do produto que deseja consultar:")
            return

        resultado = await self.buscar_produto_por_nome(texto, turn_context)
        if not resultado:
            await turn_context.send_activity("Esse produto não foi encontrado em nosso estoque.")

    async def enviar_boas_vindas(self, turn_context: TurnContext):
        card = HeroCard(
            title="🎮 Bem-vindo ao Assistente Virtual da Loja Gamer!",
            text="Estou aqui para te ajudar a encontrar os melhores consoles e ofertas.",
            buttons=[
                CardAction(type=ActionTypes.im_back, title="Ver todos os produtos", value="Ver todos os produtos"),
                CardAction(type=ActionTypes.im_back, title="Consultar Produto Específico", value="Consultar Produto Especifico"),
            ]
        )

        reply = Activity(
            type=ActivityTypes.message,
            attachments=[Attachment(
                content_type="application/vnd.microsoft.card.hero",
                content=card
            )]
        )
        await turn_context.send_activity(reply)

    async def mostrar_produtos(self, turn_context: TurnContext):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as resp:
                    if resp.status == 200:
                        produtos = await resp.json()
                        if not produtos:
                            await turn_context.send_activity("Nenhum produto encontrado.")
                            return

                        for produto in produtos:
                            await self.exibir_card_produto(turn_context, produto)
                    else:
                        await turn_context.send_activity(f"Erro ao buscar produtos: HTTP {resp.status}")
        except Exception as e:
            await turn_context.send_activity(f"Ocorreu um erro ao buscar produtos: {str(e)}")

    async def buscar_produto_por_nome(self, termo, turn_context):
        termo_extraido = self.extrair_nome_produto(termo)
        if not termo_extraido:
            return False

        termo_codificado = quote(termo_extraido)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_search_url}?nome={termo_codificado}") as resp:
                    if resp.status == 200:
                        produtos = await resp.json()
                        if not produtos:
                            return False

                        for produto in produtos:
                            await self.exibir_card_produto(turn_context, produto)
                        return True
                    else:
                        await turn_context.send_activity(f"Erro ao buscar produto: HTTP {resp.status}")
        except Exception as e:
            await turn_context.send_activity(f"Erro ao buscar produto: {str(e)}")

        return False

    def extrair_nome_produto(self, texto):
        return texto.strip() if len(texto.strip()) > 1 else None

    async def exibir_card_produto(self, turn_context, produto):
        nome = produto.get("productName", "N/A")
        descricao = produto.get("productDescription", "N/A")
        preco = produto.get("price", "N/A")
        imagem = produto.get("imageUrl", [])
        url = imagem[0] if isinstance(imagem, list) and imagem else None

        card = HeroCard(
            title=nome,
            subtitle=descricao,
            text=f"Preço: R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            images=[CardImage(url=url)] if url else []
        )

        await turn_context.send_activity(Activity(
            type=ActivityTypes.message,
            attachments=[Attachment(
                content_type="application/vnd.microsoft.card.hero",
                content=card
            )]
        ))
