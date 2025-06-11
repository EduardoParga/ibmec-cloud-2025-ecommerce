import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    TurnContext,
    MemoryStorage,
    ConversationState,
    UserState,
)
from botbuilder.schema import Activity
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter
from dialogos.bob_dialogos import BobDialogo 
from dialogos.compras_dialogos import ComprarProdutoDialog

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkHttpAdapter(SETTINGS)

# Middleware de erro
async def on_error(context: TurnContext, error: Exception):
    print(f"[on_turn_error] Unhandled error: {error}")
    await context.send_activity("Ocorreu um erro inesperado, tente novamente mais tarde.")
ADAPTER.on_turn_error = on_error

# Estados
MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)

# Bot principal
BOT = BobDialogo(CONVERSATION_STATE, USER_STATE)

# Endpoint para o bot responder mensagens
async def messages(req: web.Request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)

# Rota simples para teste no navegador
async def home(req):
    return web.Response(text="Bot está rodando!")

# Inicialização do servidor
APP = web.Application()
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/", home)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    web.run_app(APP, host="0.0.0.0", port=port)
