from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes, CardAction, ActionTypes
import aiohttp
import json

class BobDialogo(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        super(BobDialogo, self).__init__()
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.api_url = "http://localhost:8080/product"

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self.enviar_boas_vindas(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        texto = turn_context.activity.text.strip().lower()

        if "pedido" in texto:
            await turn_context.send_activity("Você escolheu Consultas de Pedidos. Ainda não implementado.")
        elif "produto" in texto or texto in ["2", "ver produtos", "quero ver produtos", "consulta de produtos"]:
            await self.mostrar_produtos(turn_context)
        elif "compra" in texto:
            await turn_context.send_activity("Você escolheu Compra de Produtos. Ainda não implementado.")
        elif "extrato" in texto:
            await turn_context.send_activity("Você escolheu Extrato de Compras. Ainda não implementado.")
        else:
            await turn_context.send_activity("Desculpe, não entendi sua escolha.")
            await self.enviar_boas_vindas(turn_context)

    async def enviar_boas_vindas(self, turn_context: TurnContext):
        card = HeroCard(
            title="Bem-vindo ao Assistente Virtual!",
            text="Escolha uma das opções abaixo:",
            buttons=[
                CardAction(type=ActionTypes.im_back, title="Consultas de Pedidos", value="Consultas de Pedidos"),
                CardAction(type=ActionTypes.im_back, title="Consulta de Produtos", value="Consulta de Produtos"),
                CardAction(type=ActionTypes.im_back, title="Compra de Produtos", value="Compra de Produtos"),
                CardAction(type=ActionTypes.im_back, title="Extrato de Compras", value="Extrato de Compras")
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
                            nome = produto.get("productName", "Nome não disponível")
                            descricao = produto.get("productDescription", "Descrição não disponível")
                            preco = produto.get("price", 0.0)
                            imagem_url = self.processar_url_imagem(produto.get("imageUrl", []))

                            card = HeroCard(
                                title=nome,
                                subtitle=descricao,
                                text=f"Preço: R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                images=[CardImage(url=imagem_url)] if imagem_url else []
                            )

                            response = Activity(
                                type=ActivityTypes.message,
                                attachments=[Attachment(
                                    content_type="application/vnd.microsoft.card.hero",
                                    content=card
                                )]
                            )
                            await turn_context.send_activity(response)
                    else:
                        await turn_context.send_activity(f"Erro ao buscar produtos: HTTP {resp.status}")
        except Exception as e:
            await turn_context.send_activity(f"Ocorreu um erro ao buscar produtos: {str(e)}")

    def processar_url_imagem(self, image_data):
        if not image_data:
            return None

        if isinstance(image_data, str) and image_data.startswith(('[', '{')):
            try:
                parsed = json.loads(image_data.replace("'", '"'))
                if isinstance(parsed, list) and len(parsed) > 0:
                    return parsed[0]
                return parsed
            except:
                return None

        if isinstance(image_data, list) and len(image_data) > 0:
            return image_data[0]

        if isinstance(image_data, str) and image_data.startswith(('http://', 'https://')):
            return image_data

        return None
