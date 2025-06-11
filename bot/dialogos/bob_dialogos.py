import aiohttp
import unicodedata
import re
import os
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes, CardAction, ActionTypes
from botbuilder.dialogs import DialogSet
from .compras_dialogos import ComprarProdutoDialog
from .extrato_dialogos import ExtratoComprasDialog
from .produtos_dialogos import ConsultarProdutosDialog
from .pedidos_dialogos import ConsultarPedidosDialog, ConsultarPedidoEspecificoDialog

PLACEHOLDER_IMG = "https://via.placeholder.com/300x200?text=Sem+Imagem"

class BobDialogo(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        super().__init__()
        self.conversation_state = conversation_state
        self.user_state = user_state
        # Endpoints públicos da API no Azure (ajustados conforme solicitado)
        self.api_url = os.getenv(
            "API_URL",
            "https://ap2big-gahqa2btgqfqhjbw.westus-01.azurewebsites.net/product"
        )
        self.api_users_url = os.getenv(
            "API_USERS_URL",
            "https://ap2big-gahqa2btgqfqhjbw.westus-01.azurewebsites.net/users"
        )
        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.dialogs = DialogSet(conversation_state.create_property("DialogState"))
        self.dialogs.add(ComprarProdutoDialog(self.user_profile_accessor))
        self.dialogs.add(ExtratoComprasDialog(self.user_profile_accessor))
        self.dialogs.add(ConsultarProdutosDialog())
        self.dialogs.add(ConsultarPedidosDialog(self.user_profile_accessor))
        self.dialogs.add(ConsultarPedidoEspecificoDialog(self.user_profile_accessor))

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Olá! Para usar o bot, faça login informando seu CPF (apenas números):")

    async def on_message_activity(self, turn_context: TurnContext):
        user_profile = await self.user_profile_accessor.get(turn_context, dict)
        if not user_profile.get("cpf"):
            cpf = turn_context.activity.text.strip()
            api_url = self.api_users_url
            id_user = None
            nome_usuario = None
            usuarios = []
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            usuarios = await resp.json()
                            for usuario in usuarios:
                                if usuario.get("cpf") == cpf:
                                    id_user = usuario.get("id")
                                    nome_usuario = usuario.get("nome", "usuário")
                                    break
            except Exception as e:
                await turn_context.send_activity(f"Erro ao validar login: {str(e)}")
                return

            if not id_user:
                await turn_context.send_activity("CPF não encontrado. Por favor, tente novamente.")
                return

            user_profile["cpf"] = cpf
            user_profile["id_user"] = id_user
            user_profile["nome"] = nome_usuario
            await self.user_profile_accessor.set(turn_context, user_profile)
            await self.user_state.save_changes(turn_context)
            await turn_context.send_activity(f"Bem-vindo, {nome_usuario}! Agora você pode usar o bot normalmente.")
            await self.enviar_boas_vindas(turn_context)
            return

        dialog_context = await self.dialogs.create_context(turn_context)
        results = await dialog_context.continue_dialog()
        if results.status.name != "Empty":
            await self.conversation_state.save_changes(turn_context)
            return

        texto = turn_context.activity.text.strip().lower()
        texto = unicodedata.normalize('NFD', texto)
        texto = texto.encode('ascii', 'ignore').decode('utf-8')
        texto = re.sub(r'[^\w\s#]', '', texto)

        # part de captura de pedido com ou sem #, sem precisar citar a palavar pedido
        match = re.search(r"(#?[pP][a-zA-Z]?\d{7,8})", texto)
        if match:
            numero_pedido = match.group(1).upper()
            await dialog_context.begin_dialog("consultar_pedido_especifico_dialog", numero_pedido)
            await self.conversation_state.save_changes(turn_context)
            return

        opcoes_pedidos = [
            "quero ver pedidos", "ver pedidos", "meus pedidos", "consultar pedidos",
            "mostrar pedidos", "listar pedidos", "historico de pedidos", "pedidos", "ver pedido"
        ]
        if any(op in texto for op in opcoes_pedidos):
            await dialog_context.begin_dialog("consultar_pedidos_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        if "extrato" in texto:
            await dialog_context.begin_dialog("extrato_compras_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        if (
            re.search(r"\bum\b", texto) or re.search(r"\buma\b", texto)
        ) and (
            "produto" in texto or "videogame" in texto or "console" in texto or "item" in texto or "jogo" in texto
        ):
            await dialog_context.begin_dialog("consultar_produtos_dialog")
            await self.conversation_state.save_changes(turn_context)
            return
        if re.search(r"\bum\b|\buma\b", texto) and any(
            palavra in texto for palavra in ["ps5", "xbox", "switch", "playstation", "nintendo"]
        ):
            await dialog_context.begin_dialog("consultar_produtos_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        if all(p in texto for p in ["ver", "produt"]):
            await self.mostrar_produtos(turn_context)
            await self.conversation_state.save_changes(turn_context)
            return

        if "comprar" in texto or "compra" in texto:
            await dialog_context.begin_dialog("comprar_produto_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        if "consultar" in texto and "produt" in texto:
            await dialog_context.begin_dialog("consultar_produtos_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        await turn_context.send_activity("Desculpe, não entendi. Por favor, escolha uma das opções do menu.")
        await self.conversation_state.save_changes(turn_context)

    async def enviar_boas_vindas(self, turn_context: TurnContext):
        card = HeroCard(
            title="🎮 Bem-vindo à MUBAK!",
            text="Estou aqui para te ajudar a encontrar os melhores consoles e ofertas.",
            buttons=[
                CardAction(type=ActionTypes.im_back, title="Ver todos os produtos", value="Ver todos os produtos"),
                CardAction(type=ActionTypes.im_back, title="Consultar Produto Específico", value="consultar produto especifico"),
                CardAction(type=ActionTypes.im_back, title="Comprar Produtos", value="comprar produtos"),
                CardAction(type=ActionTypes.im_back, title="Ver Extrato de Compras", value="ver extrato de compras"),
                CardAction(type=ActionTypes.im_back, title="Consultar Pedidos", value="consultar pedidos"),
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

                        cards = []
                        for produto in produtos:
                            nome = produto.get("nome_produto") or produto.get("productName", "Produto")
                            descricao = produto.get("descricao") or produto.get("productDescription", "")
                            descricao = descricao[:80] + "..." if len(descricao) > 80 else descricao  
                            preco = produto.get("price", 0)
                            imagem = produto.get("imageUrl", [])
                            url = imagem[0] if isinstance(imagem, list) and imagem else (imagem if isinstance(imagem, str) else None)
                            url = url or PLACEHOLDER_IMG

                            try:
                                preco_formatado = f"💰 Preço: R$ {float(preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                            except Exception:
                                preco_formatado = f"💰 Preço: R$ {preco}"

                            card = HeroCard(
                                title=f"🎮 {nome}",
                                subtitle=descricao,
                                text=preco_formatado,
                                images=[CardImage(url=url)]
                            )
                            cards.append(Attachment(
                                content_type="application/vnd.microsoft.card.hero",
                                content=card
                            ))
                        # Carroussel 
                        if len(cards) > 1:
                            await turn_context.send_activity(
                                Activity(type=ActivityTypes.message, attachments=cards, attachment_layout="carousel")
                            )
                        else:
                            for card in cards:
                                await turn_context.send_activity(
                                    Activity(type=ActivityTypes.message, attachments=[card])
                                )
                    else:
                        await turn_context.send_activity(f"Erro ao buscar produtos: HTTP {resp.status}")
        except Exception as e:
            await turn_context.send_activity(f"Ocorreu um erro ao buscar produtos: {str(e)}")

    async def exibir_card_produto(self, turn_context, produto):
        nome = produto.get("productName", "N/A")
        descricao = produto.get("productDescription", "N/A")
        descricao = descricao[:80] + "..." if len(descricao) > 80 else descricao  # Limita tamanho
        preco = produto.get("price", "N/A")
        imagem = produto.get("imageUrl", [])
        url = imagem[0] if isinstance(imagem, list) and imagem else (imagem if isinstance(imagem, str) else None)
        url = url or PLACEHOLDER_IMG

        try:
            preco_formatado = f"Preço: R$ {float(preco):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            preco_formatado = f"Preço: R$ {preco}"

        card = HeroCard(
            title=nome,
            subtitle=descricao,
            text=preco_formatado,
            images=[CardImage(url=url)]
        )

        await turn_context.send_activity(Activity(
            type=ActivityTypes.message,
            attachments=[Attachment(
                content_type="application/vnd.microsoft.card.hero",
                content=card
            )]
        ))