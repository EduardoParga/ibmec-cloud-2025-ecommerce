import aiohttp
import re
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
    def __init__(self, user_profile_accessor, dialog_id="comprar_produto_dialog"):
        super().__init__(dialog_id)
        self.user_profile_accessor = user_profile_accessor

        self.add_dialog(TextPrompt("produto_prompt"))
        self.add_dialog(TextPrompt("cartao_prompt"))
        self.add_dialog(TextPrompt("cvv_prompt"))
        self.add_dialog(
            WaterfallDialog(
                "main_dialog",
                [
                    self.perguntar_produto_step,
                    self.pedir_cartao_step,
                    self.pedir_cvv_step,
                    self.finalizar_compra_step,
                ]
            )
        )
        self.initial_dialog_id = "main_dialog"

    async def perguntar_produto_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            "produto_prompt",
            PromptOptions(prompt=MessageFactory.text(
                "🛒 Qual produto você deseja comprar?"
            ))
        )

    async def pedir_cartao_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        produto_nome = step_context.result
        step_context.values["produto_nome"] = produto_nome

        api_url = "http://localhost:8080/product"
        produto_encontrado = None
        melhor_score = 0
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        produtos = await resp.json()
                        termo_limpo = re.sub(r'[^\w\s]', '', produto_nome).lower()
                        palavras = termo_limpo.split()
                        for produto in produtos:
                            nome_candidato = (
                                produto.get("nome_produto")
                                or produto.get("productName")
                                or produto.get("nome")
                                or ""
                            ).lower()
                            descricao_candidato = (
                                produto.get("descricao")
                                or produto.get("productDescription")
                                or ""
                            ).lower()
                            score = sum(
                                (palavra in nome_candidato) or (palavra in descricao_candidato)
                                for palavra in palavras
                            )
                            if score > melhor_score:
                                melhor_score = score
                                produto_encontrado = produto
        except Exception as e:
            await step_context.context.send_activity(f"❌ Erro ao buscar produto: {str(e)}")

        if produto_encontrado and melhor_score > 0:
            nome = (
                produto_encontrado.get("nome_produto")
                or produto_encontrado.get("productName")
                or produto_encontrado.get("nome")
                or "N/A"
            )
            preco = produto_encontrado.get("price", "N/A")
            descricao = (
                produto_encontrado.get("productDescription")
                or produto_encontrado.get("descricao")
                or ""
            )
            imagem = produto_encontrado.get("imageUrl", [])
            url = imagem[0] if isinstance(imagem, list) and imagem else None

            card = HeroCard(
                title=f"🎮 {nome}",
                subtitle=descricao,
                text=f"💰 Preço: R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
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
                PromptOptions(prompt=MessageFactory.text(
                    "💳 Informe o número do cartão para pagamento:"
                ))
            )
        else:
            await step_context.context.send_activity("❗ Produto não encontrado. Tente novamente.")
            return await step_context.replace_dialog(self.initial_dialog_id)

    async def pedir_cvv_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cartao"] = step_context.result
        return await step_context.prompt(
            "cvv_prompt",
            PromptOptions(prompt=MessageFactory.text("🔒 Agora, digite o CVV do cartão:"))
        )

    async def finalizar_compra_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["cvv"] = step_context.result
        produto = step_context.values.get("produto")
        numero_cartao = step_context.values.get("cartao")
        cvv = step_context.values.get("cvv")
        valor = produto.get("price", 0)

        user_profile = await self.user_profile_accessor.get(step_context.context, dict)
        id_user = user_profile.get("id_user")

        nome_produto = (
            produto.get("nome_produto")
            or produto.get("productName")
            or produto.get("nome")
            or "Produto"
        )
        payload = {
            "numero": numero_cartao,
            "cvv": cvv,
            "valor": valor,
            "nome_produto": nome_produto
        }
   
        api_url = f"http://localhost:8080/credit_card/{id_user}/authorize"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as resp:
                    resposta = await resp.json()
                    if resp.status == 200 and resposta.get("status") == "AUTHORIZED":
                        numero_pedido = resposta.get("numero_pedido") or resposta.get("numeroPedido")
                        msg_pedido = f"\n📦 Número do pedido: {numero_pedido}" if numero_pedido else ""
                        await step_context.context.send_activity(
                            f"✅ Compra realizada com sucesso!\n\n"
                            f"🎮 Produto: *{nome_produto}*\n\n"
                            f"💰 Valor: R$ {valor:,.2f}\n\n"
                            f"{msg_pedido}\n\n"
                            f"Obrigado por comprar conosco! 😃"
                        )
                    else:
                        await step_context.context.send_activity(
                            f"❌ Compra não autorizada: {resposta.get('message', 'Erro desconhecido')}"
                        )
        except Exception as e:
            await step_context.context.send_activity(f"❌ Erro ao processar pagamento: {str(e)}")

        return await step_context.end_dialog()