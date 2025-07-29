import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from github import Github

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GIT_TOKEN")

# Initialise le client GitHub
gh = Github(GIT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salut, bot HMB-TECH est en ligne ! Tape /repos pour voir tes dépôts. Et /start pour revenir aux menus principales")

async def repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = gh.get_user()
    repos = user.get_repos()
    repo_names = [repo.name for repo in repos]
    text = "Voici tes dépôts GitHub :\n" + "\n".join(repo_names)
    await update.message.reply_text(text)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("repos", repos))

    print("🤖 Bot HMB-Tech lancé...")
    app.run_polling()