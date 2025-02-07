from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import json
import os

# Переменные для настройки
TOKEN = "XXXXXXXXXXXXXXXXXXXXXX"  # Замените на ваш токен для подключения к Telegram
CHANNEL_LINK = "https://t.me/YYYYYYYY"  # Замените на вашу ссылку на канал
DATA_FILE = 'user_data.json'

# Определение этапов для ConversationHandler
NAME, PHONE, BANK, UPDATE = range(4)

def load_user_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(user_data: dict) -> None:
    with open(DATA_FILE, 'w') as file:
        json.dump(user_data, file)

# Команда /start: регистрация или вывод текущих данных
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = load_user_data()
    chat_id = str(update.message.chat_id)
    username = update.message.from_user.username

    if chat_id in user_data:
        user = user_data[chat_id]
        user_info = (
            f"Ваши данные:\nИмя и Фамилия: {user['name']}\nТелефон: {user['phone']}\nБанк: {user['bank']}\n"
            f"Username: @{username}\n"
            f"Если вы хотите обновить информацию о себе, используйте команду /update. "
            f"Если вы хотите выйти из сообщества, используйте команду /leave."
        )
        await update.message.reply_text(user_info)
    else:
        await update.message.reply_text(
            "Привет! Пожалуйста, введите ваше Имя и Фамилию:\n\n"
        )
        return NAME
    return ConversationHandler.END

# Получение имени
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Спасибо! Теперь введите ваш номер телефона:")
    return PHONE

# Получение телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Отлично! Теперь введите название банка для переводов:")
    return BANK

# Получение банка
async def get_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['bank'] = update.message.text

    user_data = load_user_data()
    chat_id = str(update.message.chat_id)
    username = update.message.from_user.username

    # Обновление данных пользователя или создание новой записи
    if chat_id in user_data:
        user_data[chat_id].update(context.user_data)
    else:
        user_data[chat_id] = context.user_data.copy()
        user_data[chat_id]['username'] = username

    save_user_data(user_data)
    
    await update.message.reply_text(f"Спасибо! Вы зарегистрированы. Вот ссылка на закрытый канал: {CHANNEL_LINK}")
    return ConversationHandler.END

# Команда для обновления данных
async def update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = load_user_data()
    chat_id = str(update.message.chat_id)

    if chat_id in user_data:
        await update.message.reply_text("Вы выбрали обновление данных. Пожалуйста, введите новое Имя и Фамилию:")
        return NAME
    else:
        await update.message.reply_text("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")
        return ConversationHandler.END

# Команда для удаления пользователя из списка
async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = load_user_data()
    chat_id = str(update.message.chat_id)

    if chat_id in user_data:
        del user_data[chat_id]  # Удаляем пользователя из словаря
        save_user_data(user_data)  # Сохраняем обновленные данные
        await update.message.reply_text("Ваши данные удалены из системы.")
    else:
        await update.message.reply_text("Вы не зарегистрированы в системе.")

# Fallback для отмены процесса регистрации
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Регистрация отменена. Если хотите попробовать снова, введите /start.")
    return ConversationHandler.END

# Главная функция для запуска бота
def main():
    application = Application.builder().token(TOKEN).build()

    # Создание ConversationHandler для процесса регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('update', update)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            BANK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_bank)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Добавляем новый обработчик для команды /leave
    application.add_handler(CommandHandler('leave', leave))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
