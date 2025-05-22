from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import HeroCard, CardAction, ActionTypes
from .produtos_dialogos import ConsultarProdutosDialog

class MainDialogos(ComponentDialog):
    def __init__(self, dialog_id: str = "main_dialogos"):
        super(MainDialogos, self).__init__(dialog_id)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConsultarProdutosDialog())

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
        card = HeroCard(
            text="Escolha uma opção:",
            buttons=[
                CardAction(title="Consultar Produtos", type=ActionTypes.im_back, value="consultar produtos"),
                CardAction(title="Consultas de Pedidos", type=ActionTypes.im_back, value="consultas de pedidos"),
                CardAction(title="Compra de Produtos", type=ActionTypes.im_back, value="compra de produtos"),
                CardAction(title="Extrato de Compras", type=ActionTypes.im_back, value="extrato de compras"),
                CardAction(title="Sair", type=ActionTypes.im_back, value="sair"),
            ]
        )

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.attachment(card.to_attachment())),
        )

    async def processar_escolha_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        escolha = step_context.result.strip().lower()

        if "consultar" in escolha and "produto" in escolha:
            return await step_context.begin_dialog("consultar_produtos_dialog")
        elif "sair" in escolha:
            await step_context.context.send_activity("Até logo!")
            return await step_context.end_dialog()
        else:
            await step_context.context.send_activity("Opção inválida, tente novamente.")
            return await step_context.replace_dialog(self.id)