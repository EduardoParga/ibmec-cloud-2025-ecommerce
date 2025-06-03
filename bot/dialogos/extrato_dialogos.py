import aiohttp
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.core import MessageFactory

class ExtratoComprasDialog(ComponentDialog):
    def __init__(self, dialog_id: str = "extrato_compras_dialog"):
        super(ExtratoComprasDialog, self).__init__(dialog_id)

        self.add_dialog(WaterfallDialog(
            "waterfall",
            [self.exibir_extrato_step, self.encerrar_step]
        ))

        self.initial_dialog_id = "waterfall"

    async def exibir_extrato_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/compras/extrato") as resp:
                    if resp.status == 200:
                        extrato = await resp.json()
                        if not extrato:
                            await step_context.context.send_activity("Você ainda não possui compras registradas.")
                        else:
                            for item in extrato:
                                await step_context.context.send_activity(
                                    f"{item.get('data', 'sem data')}: {item.get('produto', 'sem nome')} - R$ {item.get('valor', 0):.2f}"
                                )
                    else:
                        await step_context.context.send_activity("Erro ao buscar extrato de compras.")
        except Exception as e:
            await step_context.context.send_activity(f"Erro de conexão: {str(e)}")

        return await step_context.next(None)

    async def encerrar_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Extrato finalizado. Caso deseje mais detalhes, posso ajudar!")
        return await step_context.end_dialog()
