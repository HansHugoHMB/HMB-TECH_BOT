import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from github import Github
from github.GithubException import GithubException

# Configuration des tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GIT_TOKEN")

if not BOT_TOKEN or not GITHUB_TOKEN:
    raise ValueError("Les tokens BOT_TOKEN et GIT_TOKEN doivent être définis dans les variables d'environnement")

# Initialisation de l'API GitHub
try:
    gh = Github(GITHUB_TOKEN)
except Exception as e:
    print(f"Erreur lors de l'initialisation de l'API GitHub: {e}")
    raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "👋 Salut, bot HMB-TECH est en ligne ! "
            "Tape /repos pour voir tes dépôts. "
            "Et /start pour revenir aux menus principales"
        )
    except Exception as e:
        print(f"Erreur lors de la commande start: {e}")
        await update.message.reply_text("Une erreur est survenue")

async def repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = gh.get_user()
        repos = user.get_repos()
        repo_names = [repo.name for repo in repos]
        text = "Voici tes dépôts GitHub :\n" + "\n".join(repo_names)
        await update.message.reply_text(text)
    except GithubException as e:
        print(f"Erreur GitHub: {e}")
        await update.message.reply_text("Erreur lors de la récupération des dépôts GitHub")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        await update.message.reply_text("Une erreur inattendue est survenue")

def main():
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("repos", repos))

        print("🤖 Bot HMB-Tech lancé...")
        app.run_polling()
    except Exception as e:
        print(f"Erreur fatale: {e}")

if __name__ == "__main__":
    main()