import aiohttp
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory

class ConsultarProdutosDialog(ComponentDialog):
    def __init__(self, dialog_id: str = "consultar_produtos_dialog"):
        super(ConsultarProdutosDialog, self).__init__(dialog_id)

        self.add_dialog(TextPrompt("text_prompt"))
        self.add_dialog(
            WaterfallDialog(
                "waterfall",
                [
                    self.mostrar_produtos_step,
                    self.encerrar_dialogo_step,
                ],
            )
        )
        self.initial_dialog_id = "waterfall"

    async def mostrar_produtos_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Buscando produtos disponíveis...")

        api_url = "http://localhost:8080/products"  

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status == 200:
                    produtos = await resp.json()
                    if not produtos:
                        await step_context.context.send_activity("Nenhum produto encontrado.")
                    else:
                        for p in produtos:
                            texto = f"**{p['nome']}**\nDescrição: {p['descricao']}\nPreço: R$ {p['preco']:.2f}"
                            await step_context.context.send_activity(texto)
                else:
                    await step_context.context.send_activity("Erro ao acessar a API de produtos.")
        return await step_context.next(None)

    async def encerrar_dialogo_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Consulta finalizada! Se precisar, é só chamar.")
        return await step_context.end_dialog()
