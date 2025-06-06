import aiohttp
import urllib.parse
import re
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    TextPrompt,
    PromptOptions
)
from botbuilder.core import MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes

class ConsultarProdutosDialog(ComponentDialog):
    def __init__(self, dialog_id="consultar_produtos_dialog"):
        super().__init__(dialog_id)
        self.add_dialog(TextPrompt("busca_produto_prompt"))
        self.add_dialog(
            WaterfallDialog(
                "main_dialog",
                [
                    self.perguntar_termo_busca_step,
                    self.mostrar_resultados_step,
                ]
            )
        )
        self.initial_dialog_id = "main_dialog"

    async def perguntar_termo_busca_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "busca_produto_prompt",
            PromptOptions(prompt=MessageFactory.text("🔎 Qual produto você procura?"))
        )

    async def mostrar_resultados_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        termo = step_context.result.strip()
        termo_limpo = re.sub(r'[^\w\s]', '', termo)
        termo_encoded = urllib.parse.quote(termo_limpo)

        api_url = f"http://localhost:8080/product/search?termo={termo_encoded}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        produtos = await resp.json()
                        if not produtos:
                            await step_context.context.send_activity("❌ Nenhum produto encontrado para sua busca.")
                        else:
                            cards = []
                            for produto in produtos:
                                nome = produto.get('nome_produto') or produto.get('productName', 'Produto')
                                descricao = produto.get('descricao') or produto.get('productDescription', '')
                                preco = produto.get('price', 0)
                                imagem = produto.get('imageUrl', [])

                                url = imagem[0] if isinstance(imagem, list) and imagem else (imagem if isinstance(imagem, str) else None)

                                card = HeroCard(
                                    title=f"🎮 {nome}",
                                    subtitle=descricao,
                                    text=f"💰 Preço: R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                    images=[CardImage(url=url)] if url else []
                                )
                                cards.append(Attachment(
                                    content_type="application/vnd.microsoft.card.hero",
                                    content=card
                                ))
                            # Envia todos os cards em um carrossel se houver mais de um produto
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
                        await step_context.context.send_activity("⚠️ Erro ao buscar produtos.")
        except Exception as e:
            await step_context.context.send_activity(f"⚠️ Erro ao buscar produtos: {str(e)}")

        return await step_context.end_dialog()