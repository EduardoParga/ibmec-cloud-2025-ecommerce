import aiohttp
from datetime import datetime
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.core import MessageFactory

class ExtratoComprasDialog(ComponentDialog):
    def __init__(self, user_profile_accessor=None, dialog_id="extrato_compras_dialog"):
        super().__init__(dialog_id)
        self.user_profile_accessor = user_profile_accessor

        self.add_dialog(
            WaterfallDialog(
                "main_dialog",
                [
                    self.mostrar_extrato_step,
                    self.encerrar_dialogo_step,
                ]
            )
        )
        self.initial_dialog_id = "main_dialog"

    async def mostrar_extrato_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        id_user = None
        if self.user_profile_accessor:
            user_profile = await self.user_profile_accessor.get(step_context.context, dict)
            id_user = user_profile.get("id_user")

        if not id_user:
            await step_context.context.send_activity("Não foi possível identificar o usuário. Faça login novamente.")
            return await step_context.end_dialog()

        api_url = f"http://localhost:8080/purchase/{id_user}/extract"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        extrato = await resp.json()
                        if not extrato:
                            await step_context.context.send_activity("Você ainda não realizou nenhuma compra.")
                        else:
                            linhas = []
                            for compra in extrato:
                                nome = compra.get('nome_produto', 'Produto')
                                valor = compra.get('price', 0)
                                data_raw = compra.get('dtCompra', '')
                                # Formata a data
                                try:
                                    data_fmt = datetime.fromisoformat(data_raw).strftime('%d/%m/%Y %H:%M')
                                except Exception:
                                    data_fmt = data_raw
                                linhas.append(f"• {nome}\n   Valor: R$ {valor:,.2f}\n   Data: {data_fmt}")
                            mensagem = "🧾 **Extrato de Compras:**\n\n" + "\n\n".join(linhas)
                            await step_context.context.send_activity(mensagem)
                    else:
                        await step_context.context.send_activity("Erro ao buscar extrato de compras.")
        except Exception as e:
            await step_context.context.send_activity(f"Erro ao buscar extrato de compras: {str(e)}")

        return await step_context.next(None)

    async def encerrar_dialogo_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Extrato finalizado. Caso deseje mais detalhes, posso ajudar!")
        return await step_context.end_dialog()