import os
import ast
import operator
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("8957410762:AAFLQKv6z4wE0oNmtHItJfzGQnPoOK0zM7U")

# عملگرهای مجاز
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op = OPS.get(type(node.op))
        if not op:
            raise ValueError("عملگر غیرمجاز")
        return op(safe_eval(node.left), safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = OPS.get(type(node.op))
        if not op:
            raise ValueError("عملگر غیرمجاز")
        return op(safe_eval(node.operand))
    raise ValueError("عبارت نامعتبر")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام")

async def calc_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # فقط اگه شامل عدد و عملگر بود حساب کن
    allowed = set("0123456789+-*/(). %")
    if not all(ch in allowed for ch in text):
        return  # پیام معمولی، نادیده بگیر

    try:
        tree = ast.parse(text, mode="eval")
        result = safe_eval(tree)
        await update.message.reply_text(f"{result}")
    except Exception:
        return  # اگه عبارت معتبر نبود، جواب نده

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

# هر پیام متنی که دستور نیست رو بگیر
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calc_message))

app.run_polling()
