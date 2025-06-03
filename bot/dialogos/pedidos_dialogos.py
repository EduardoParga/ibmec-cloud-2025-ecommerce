from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.core import MessageFactory
import aiohttp

class ConsultarPedidosDialog(ComponentDialog):
    def __init__(self, dialog_id: str = "consultar_pedidos_dialog"):
        super(ConsultarPedidosDialog, self).__init__(dialog_id)

        self.add_dialog(WaterfallDialog(
            "waterfall",
            [self.exibir_pedidos_step, self.encerrar_step]
        ))

        self.initial_dialog_id = "waterfall"

    async def exibir_pedidos_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/compras/pedidos") as resp:
                    if resp.status == 200:
                        pedidos = await resp.json()
                        if not pedidos:
                            await step_context.context.send_activity("Nenhum pedido encontrado.")
                        else:
                            for pedido in pedidos:
                                await step_context.context.send_activity(
                                    f"Pedido #{pedido.get('id')}: {pedido.get('produto')} - Status: {pedido.get('status')} - R$ {pedido.get('valor'):.2f}"
                                )
                    else:
                        await step_context.context.send_activity("Erro ao buscar pedidos.")
        except Exception as e:
            await step_context.context.send_activity(f"Erro de conexão: {str(e)}")

        return await step_context.next(None)

    async def encerrar_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Consulta finalizada!")
        return await step_context.end_dialog()
