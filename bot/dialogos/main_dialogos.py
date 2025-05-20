from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from .produtos_dialogos import ConsultarProdutosDialog

class MainDialogos(ComponentDialog):
    def __init__(self, dialog_id: str = "main_dialogos"):
        super(MainDialogos, self).__init__(dialog_id)

        # Adiciona o diálogo de produtos
        self.add_dialog(ConsultarProdutosDialog())

        # Diálogo principal em waterfall (exemplo simples)
        self.add_dialog(
            WaterfallDialog(
                "main_waterfall",
                [
                    self.menu_step,
                    self.processar_escolha_step,
                ],
            )
        )

        self.initial_dialog_id = "main_waterfall"

    async def menu_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        mensagem = (
            "Escolha uma opção:\n\n"
            "1️⃣  - Consultar Produtos\n"
            "0️⃣  - Sair"
        )
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text(mensagem)),
        )

    async def processar_escolha_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        escolha = step_context.result.strip()

        if escolha == "1":
            # Iniciar o diálogo de consulta de produtos
            return await step_context.begin_dialog("consultar_produtos_dialog")
        elif escolha == "0":
            await step_context.context.send_activity("Até logo!")
            return await step_context.end_dialog()
        else:
            await step_context.context.send_activity("Opção inválida, tente novamente.")
            return await step_context.replace_dialog(self.id)
