import aiohttp
import unicodedata
import re
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes, CardAction, ActionTypes
from botbuilder.dialogs import DialogSet
from .compras_dialogos import ComprarProdutoDialog
from .extrato_dialogos import ExtratoComprasDialog
from .produtos_dialogos import ConsultarProdutosDialog

class BobDialogo(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        super().__init__()
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.api_url = "http://localhost:8080/product"
        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.dialogs = DialogSet(conversation_state.create_property("DialogState"))
        self.dialogs.add(ComprarProdutoDialog(self.user_profile_accessor))
        self.dialogs.add(ExtratoComprasDialog(self.user_profile_accessor))
        self.dialogs.add(ConsultarProdutosDialog())

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Olá! Para usar o bot, faça login informando seu CPF (apenas números):")

    async def on_message_activity(self, turn_context: TurnContext):
        user_profile = await self.user_profile_accessor.get(turn_context, dict)
        if not user_profile.get("cpf"):
            cpf = turn_context.activity.text.strip()
            api_url = "http://localhost:8080/users"
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
        # Remove acentos e sinais
        texto = unicodedata.normalize('NFD', texto)
        texto = texto.encode('ascii', 'ignore').decode('utf-8')
        texto = re.sub(r'[^\w\s]', '', texto)

        # 1. Produto específico (singular) - DEVE vir antes!
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

        # 2. Ver todos os produtos
        if all(p in texto for p in ["ver", "produt"]):
            await self.mostrar_produtos(turn_context)
            await self.conversation_state.save_changes(turn_context)
            return

        # 3. Comprar produtos
        if "comprar" in texto or "compra" in texto:
            await dialog_context.begin_dialog("comprar_produto_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        # 4. Consultar produto específico por outros termos
        if "consultar" in texto and "produt" in texto:
            await dialog_context.begin_dialog("consultar_produtos_dialog")
            await self.conversation_state.save_changes(turn_context)
            return

        # 5. Extrato
        if "extrato" in texto or "pedido" in texto:
            await dialog_context.begin_dialog("extrato_compras_dialog")
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