import aiohttp
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
    def __init__(self, dialog_id: str = "consultar_produtos_dialog"):
        super(ConsultarProdutosDialog, self).__init__(dialog_id)

        self.add_dialog(TextPrompt("text_prompt"))
        self.add_dialog(
            WaterfallDialog(
                "waterfall",
                [
                    self.perguntar_nome_produto_step,
                    self.mostrar_produtos_step,
                    self.encerrar_dialogo_step,
                ],
            )
        )
        self.initial_dialog_id = "waterfall"

    async def perguntar_nome_produto_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "text_prompt",
            PromptOptions(prompt=MessageFactory.text("Qual produto você deseja pesquisar?"))
        )

    async def mostrar_produtos_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        nome_produto = step_context.result
      

        api_url = f"http://localhost:8080/product/search?nome={nome_produto}"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    produtos = await resp.json()
                    if not produtos:
                        await step_context.context.send_activity("Nenhum produto encontrado.")
                    else:
                        for p in produtos:
                            nome = p.get('productName', p.get('nome', ''))
                            descricao = p.get('productDescription', p.get('descricao', p.get('description', '')))
                            preco = p.get('price', p.get('preco', 0))
                            imagem = p.get('imageUrl', [])
                            url = imagem[0] if isinstance(imagem, list) and imagem else None

                            card = HeroCard(
                                title=nome,
                                subtitle=descricao,
                                text=f"Preço: R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                images=[CardImage(url=url)] if url else []
                            )
                            await step_context.context.send_activity(Activity(
                                type=ActivityTypes.message,
                                attachments=[Attachment(
                                    content_type="application/vnd.microsoft.card.hero",
                                    content=card
                                )]
                            ))
                else:
                    await step_context.context.send_activity("Erro ao acessar a API de produtos.")
        return await step_context.next(None)

    async def encerrar_dialogo_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Consulta finalizada! Se precisar, é só chamar.")
        return await step_context.end_dialog()