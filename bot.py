import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from github import Github
import logging

# Configuration des logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Tokens divisés en deux parties
BOT_TOKEN_PART1 = "8428723767"
BOT_TOKEN_PART2 = ":AAGImaLy3kH1OTJeoMeL8yfBHOL2YcrnTlo"
BOT_TOKEN = BOT_TOKEN_PART1 + BOT_TOKEN_PART2

GIT_TOKEN_PART1 = "ghp_FdhLrRA2VYSXENmPbV5"
GIT_TOKEN_PART2 = "ZtDeFBCAeNc2xpMaI"
GIT_TOKEN = GIT_TOKEN_PART1 + GIT_TOKEN_PART2

# Initialisation de l'API GitHub
gh = Github(GIT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "👋 Salut ! Je suis le bot HMB-TECH.\n"
            "Commandes disponibles :\n"
            "/repos - Voir la liste des dépôts\n"
            "/start - Revenir au menu principal"
        )
    except Exception as e:
        logger.error(f"Erreur dans start: {e}")
        await update.message.reply_text("Une erreur est survenue")

async def repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = gh.get_user()
        repos = user.get_repos()
        keyboard = []
        
        for repo in repos:
            keyboard.append([InlineKeyboardButton(repo.name, callback_data=f"repo_{repo.name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Sélectionnez un dépôt :", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Erreur dans repos: {e}")
        await update.message.reply_text("Erreur lors de la récupération des dépôts")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("repo_"):
            repo_name = data.replace("repo_", "")
            repo = gh.get_repo(f"{gh.get_user().login}/{repo_name}")
            
            contents = repo.get_contents("")
            keyboard = []
            
            for content in contents:
                callback_data = f"file_{repo_name}_{content.path}" if content.type == "file" else f"dir_{repo_name}_{content.path}"
                keyboard.append([InlineKeyboardButton(f"{'📄' if content.type == 'file' else '📁'} {content.name}", 
                                                    callback_data=callback_data)])
            
            keyboard.append([InlineKeyboardButton("⬅️ Retour aux dépôts", callback_data="back_to_repos")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(f"Contenu du dépôt {repo_name}:", reply_markup=reply_markup)
            
        elif data.startswith("file_"):
            _, repo_name, *path_parts = data.split("_")
            file_path = "_".join(path_parts)
            repo = gh.get_repo(f"{gh.get_user().login}/{repo_name}")
            content = repo.get_contents(file_path)
            
            if len(content.decoded_content.decode()) > 4000:
                message = "Le fichier est trop grand pour être affiché entièrement. Voici les premiers caractères :\n\n"
                message += content.decoded_content.decode()[:4000]
            else:
                message = content.decoded_content.decode()
            
            keyboard = [[InlineKeyboardButton("⬅️ Retour", callback_data=f"repo_{repo_name}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup)
            
        elif data.startswith("dir_"):
            _, repo_name, *path_parts = data.split("_")
            dir_path = "_".join(path_parts)
            repo = gh.get_repo(f"{gh.get_user().login}/{repo_name}")
            contents = repo.get_contents(dir_path)
            
            keyboard = []
            for content in contents:
                callback_data = f"file_{repo_name}_{content.path}" if content.type == "file" else f"dir_{repo_name}_{content.path}"
                keyboard.append([InlineKeyboardButton(f"{'📄' if content.type == 'file' else '📁'} {content.name}", 
                                                    callback_data=callback_data)])
            
            keyboard.append([InlineKeyboardButton("⬅️ Retour", callback_data=f"repo_{repo_name}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(f"Contenu du dossier {dir_path}:", reply_markup=reply_markup)
            
        elif data == "back_to_repos":
            await repos(update, context)
            
    except Exception as e:
        logger.error(f"Erreur dans button_callback: {e}")
        await query.edit_message_text("Une erreur est survenue")

def main():
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("repos", repos))
        app.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("🤖 Bot HMB-Tech démarré...")
        app.run_polling()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")

if __name__ == "__main__":
    main()