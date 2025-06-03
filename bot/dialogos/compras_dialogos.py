import aiohttp
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    TextPrompt,
    PromptOptions,
)
from botbuilder.core import MessageFactory
from botbuilder.schema import HeroCard, CardImage, Attachment, Activity, ActivityTypes

class ComprarProdutoDialog(ComponentDialog):
    def __init__(self, dialog_id="comprar_produto_dialog"):
        super().__init__(dialog_id)

        self.add_dialog(TextPrompt("produto_prompt"))
        self.add_dialog(TextPrompt("cartao_prompt"))
        self.add_dialog(TextPrompt("validade_prompt"))
        self.add_dialog(TextPrompt("cvv_prompt"))
        self.add_dialog(
            WaterfallDialog(
                "main_dialog",
                [
                    self.perguntar_produto_step,
                    self.pedir_cartao_step,
                    self.pedir_validade_step,
                    self.pedir_cvv_step,
                    self.finalizar_compra_step,
                ]
            )
        )
        self.initial_dialog_id = "main_dialog"

    async def perguntar_produto_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "produto_prompt",
            PromptOptions(prompt=MessageFactory.text("Qual produto você deseja comprar?"))
        )

    async def pedir_cartao_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        produto_nome = step_context.result
        step_context.values["produto_nome"] = produto_nome

        # Busca produto na API para mostrar detalhes
        api_url = "http://localhost:8080/product"
        produto_encontrado = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        produtos = await resp.json()
                        for produto in produtos:
                            if produto_nome.lower() in produto.get("productName", "").lower():
                                produto_encontrado = produto
                                break
        except Exception as e:
            await step_context.context.send_activity(f"Erro ao buscar produto: {str(e)}")

        if produto_encontrado:
            nome = produto_encontrado.get("productName", "N/A")
            preco = produto_encontrado.get("price", "N/A")
            descricao = produto_encontrado.get("productDescription", "N/A")
            imagem = produto_encontrado.get("imageUrl", [])
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

            step_context.values["produto"] = produto_encontrado
            return await step_context.prompt(
                "cartao_prompt",
                PromptOptions(prompt=MessageFactory.text("Informe o número do cartão:"))
            )
        else:
            await step_context.context.send_activity("Produto não encontrado. Tente novamente.")
            return await step_context.replace_dialog(self.initial_dialog_id)

    async def pedir_validade_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cartao"] = step_context.result
        return await step_context.prompt(
            "validade_prompt",
            PromptOptions(prompt=MessageFactory.text("Informe a validade do cartão (MM/AA):"))
        )

    async def pedir_cvv_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["validade"] = step_context.result
        return await step_context.prompt(
            "cvv_prompt",
            PromptOptions(prompt=MessageFactory.text("Informe o CVV do cartão:"))
        )

    async def finalizar_compra_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cvv"] = step_context.result
        produto = step_context.values.get("produto")
        if produto:
            await step_context.context.send_activity(
                f"Compra do produto '{produto.get('productName', 'N/A')}' realizada com sucesso!\nObrigado pela preferência."
            )
        else:
            await step_context.context.send_activity("Não foi possível finalizar a compra.")
        return await step_context.end_dialog()