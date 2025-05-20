from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ActivityTypes
import aiohttp

class BobTheBot(ActivityHandler):
    def __init__(self, conversation_state, user_state):
        super().__init__()
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.api_url = "http://localhost:8080/produtos"  

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Olá! Bem-vindo ao nosso bot. Por favor, escolha uma opção:\n\n"
                                                 "1 - Consultas de Pedidos\n\n"
                                                 "2 - Consulta de Produtos\n\n"
                                                 "3 - Compra de Produtos\n\n"
                                                 "4 - Extrato de Compras")

    async def on_message_activity(self, turn_context: TurnContext):
        texto_usuario = turn_context.activity.text.strip()

        if texto_usuario == "1":
            await turn_context.send_activity("Você escolheu Consultas de Pedidos. Ainda não implementado.")
        elif texto_usuario == "2":
         
            await self.mostrar_produtos(turn_context)
        elif texto_usuario == "3":
            await turn_context.send_activity("Você escolheu Compra de Produtos. Ainda não implementado.")
        elif texto_usuario == "4":
            await turn_context.send_activity("Você escolheu Extrato de Compras. Ainda não implementado.")
        else:
            await turn_context.send_activity("Opção inválida. Por favor, escolha:\n"
                                             "1 - Consultas de Pedidos\n"
                                             "2 - Consulta de Produtos\n"
                                             "3 - Compra de Produtos\n"
                                             "4 - Extrato de Compras")

    async def mostrar_produtos(self, turn_context: TurnContext):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as resp:
                    if resp.status == 200:
                        produtos = await resp.json()
                        if not produtos:
                            await turn_context.send_activity("Nenhum produto encontrado.")
                            return
                        
                        resposta = "Produtos disponíveis:\n\n"
                        for p in produtos:
                          
                            resposta += (f"Nome: {p.get('nome', 'N/A')}\n"
                                         f"Descrição: {p.get('descricao', 'N/A')}\n"
                                         f"Preço: R$ {p.get('preco', 'N/A')}\n"
                                         f"Foto: {p.get('foto', 'N/A')}\n\n")
                        await turn_context.send_activity(resposta)
                    else:
                        await turn_context.send_activity(f"Erro ao buscar produtos: {resp.status}")
        except Exception as e:
            await turn_context.send_activity(f"Ocorreu um erro ao buscar produtos: {str(e)}")
