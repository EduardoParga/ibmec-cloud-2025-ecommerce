from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.core import MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes
import aiohttp
from datetime import datetime
import random

class ConsultarPedidosDialog(ComponentDialog):
    def __init__(self, user_profile_accessor=None, dialog_id: str = "consultar_pedidos_dialog"):
        super().__init__(dialog_id)
        self.user_profile_accessor = user_profile_accessor

        self.add_dialog(WaterfallDialog(
            "waterfall",
            [self.exibir_pedidos_step, self.encerrar_step]
        ))

        self.initial_dialog_id = "waterfall"

    async def exibir_pedidos_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = None
        if self.user_profile_accessor:
            user_profile = await self.user_profile_accessor.get(step_context.context, dict)
            id_user = user_profile.get("id_user")

        if not id_user:
            await step_context.context.send_activity("Não foi possível identificar o usuário. Faça login novamente.")
            return await step_context.end_dialog()

        api_url = f"http://localhost:8080/purchase/{id_user}/orders"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        pedidos = await resp.json()
                        if not pedidos:
                            await step_context.context.send_activity("Você ainda não fez nenhum pedido.")
                        else:
                            cards = []
                            for pedido in pedidos:
                                nome = pedido.get('nome_produto') or pedido.get('productName', 'Produto')
                                valor = pedido.get('price', 0)
                                data_raw = pedido.get('dtCompra', '')
                                try:
                                    data_fmt = datetime.fromisoformat(data_raw).strftime('%d/%m/%Y %H:%M')
                                except Exception:
                                    data_fmt = data_raw
                                imagem = pedido.get('imageUrl', [])
                                url = imagem[0] if isinstance(imagem, list) and imagem else (imagem if isinstance(imagem, str) else None)
                                numero_pedido = pedido.get('numeroPedido') or pedido.get('numero_pedido', '')

                                status = random.choice(["Em separação", "Em transporte", "Entregue"])

                                card = HeroCard(

                                    subtitle=f"💰 Valor: R$ {valor:,.2f}\n📅 Data: {data_fmt}",
                                    images=[CardImage(url=url)] if url else [],
                                    text=f"📦 Número do pedido: {numero_pedido}\n\n🚚 Status: {status}" if numero_pedido else f"🚚 Status: {status}"
                                )
                                cards.append(Attachment(
                                    content_type="application/vnd.microsoft.card.hero",
                                    content=card
                                ))
                            # Envia todos os cards em um carrossel se houver mais de um pedido
                            if len(cards) > 1:
                                await step_context.context.send_activity(
                                    Activity(type=ActivityTypes.message, attachments=cards, attachment_layout="carousel")
                                )
                            else:
                                for card in cards:
                                    await step_context.context.send_activity(
                                        Activity(type=ActivityTypes.message, attachments=[card])
                                    )
                    else:
                        await step_context.context.send_activity("Erro ao buscar pedidos.")
        except Exception as e:
            await step_context.context.send_activity(f"Erro de conexão: {str(e)}")

        return await step_context.next(None)

    async def encerrar_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Consulta de pedidos finalizada!")
        return await step_context.end_dialog()


class ConsultarPedidoEspecificoDialog(ComponentDialog):
    def __init__(self, user_profile_accessor=None, dialog_id: str = "consultar_pedido_especifico_dialog"):
        super().__init__(dialog_id)
        self.user_profile_accessor = user_profile_accessor

        self.add_dialog(WaterfallDialog(
            "waterfall",
            [self.exibir_pedido_step, self.encerrar_step]
        ))

        self.initial_dialog_id = "waterfall"

    async def exibir_pedido_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = None
        if self.user_profile_accessor:
            user_profile = await self.user_profile_accessor.get(step_context.context, dict)
            id_user = user_profile.get("id_user")

        numero_pedido = step_context.options if step_context.options else None

        if not id_user or not numero_pedido:
            await step_context.context.send_activity("Não foi possível identificar o usuário ou o número do pedido.")
            return await step_context.end_dialog()

        if numero_pedido.startswith("#"):
            numero_pedido_url = numero_pedido[1:]
        else:
            numero_pedido_url = numero_pedido

        api_url = f"http://localhost:8080/purchase/{id_user}/orders/{numero_pedido_url}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        pedido = await resp.json()
                        nome = pedido.get('nome_produto') or pedido.get('productName', 'Produto')
                        valor = pedido.get('price', 0)
                        data_raw = pedido.get('dtCompra', '')
                        try:
                            data_fmt = datetime.fromisoformat(data_raw).strftime('%d/%m/%Y %H:%M')
                        except Exception:
                            data_fmt = data_raw
                        imagem = pedido.get('imageUrl', [])
                        url = imagem[0] if isinstance(imagem, list) and imagem else (imagem if isinstance(imagem, str) else None)
                        numero_pedido_card = pedido.get('numeroPedido') or pedido.get('numero_pedido', '')

                        status = random.choice(["Em separação", "Em transporte", "Entregue"])

                        card = HeroCard(
                            subtitle=f"🎮 Produto: {nome}\n💰 Valor: R$ {valor:,.2f}\n📅 Data: {data_fmt}",
                            images=[CardImage(url=url)] if url else [],
                            text=f"📦 Número do pedido: {numero_pedido_card}\n🚚 Status: {status}" if numero_pedido_card else f"🚚 Status: {status}"
                        )
                        await step_context.context.send_activity(Activity(
                            type=ActivityTypes.message,
                            attachments=[Attachment(
                                content_type="application/vnd.microsoft.card.hero",
                                content=card
                            )]
                        ))
                    elif resp.status == 404:
                        await step_context.context.send_activity("Pedido não encontrado.")
                    else:
                        await step_context.context.send_activity("Erro ao buscar o pedido.")
        except Exception as e:
            await step_context.context.send_activity(f"Erro de conexão: {str(e)}")

        return await step_context.next(None)

    async def encerrar_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Consulta de pedido finalizada!")
        return await step_context.end_dialog()