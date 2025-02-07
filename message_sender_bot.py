import json
import random
import requests

# Переменные для настройки
TOKEN = "XXXXXXXXXXXXXXXXXXXX"  # Замените на ваш токен для подключения к Telegram
CHANNEL_ID = -11111111111111  # Замените на ваш ID канала
DATA_FILE = 'user_data.json'

def send_weekly_message():
    # Загрузка данных о пользователях
    with open(DATA_FILE, 'r') as file:
        user_data = json.load(file)
    
    # Выбор случайного пользователя
    user_id = random.choice(list(user_data.keys()))
    user = user_data[user_id]

    # Формирование сообщения
    message = (
        f"На следующую неделю сбором средств занимается {user['name']} "u'\U00002757'"  "
        f"Переведите ему 150 рублей по номеру {user['phone']} в банк {user['bank']} , также к переводу или здесь в чате можно указать (названия)ссылки на конкретные вкусняхи из KDV "u'\U0001F369'"  "
        f"@{user['username']}  не забудь заказать в kdvonline вкусняшки на всех, постарайся взять поразнообразней и учитывай пожелание ребят в комментах. "
        f"Заказывай доставку на понедельник 10:30, мы все на тебя надеемся "u'\U0001F600'" "
        f"Кто уже перевел отмечайтесь реакцией "u'\U0001F44C'" в этом треде, кто будет в понедельник в офисе и сможет принять доставку напишите комментом ! "
    )

    # Отправка сообщения в канал через Telegram API
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"  # Используем HTML для обработки упоминаний
    }
    response = requests.post(url, data=data)

    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")

if __name__ == '__main__':
    send_weekly_message()
