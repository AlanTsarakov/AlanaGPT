from yandex_cloud_ml_sdk import YCloudML #Импорт API Яндекса 

import telebot
from telebot import types

import requests




with open('keys.txt', 'r', encoding='utf-8') as file:
    keys = file.read().split()

folder_id = keys[1]
api_yandex_key = keys[2]


chat_history = {}

bot = telebot.TeleBot(keys[0])
sdk = YCloudML(
    folder_id=folder_id, auth=api_yandex_key
)
@bot.message_handler(commands=['start'])
def start(message):
        hello_message = """Салам, мӕ зынаргъ хӕлар! ✨
Ӕз дӕн Аланӕ, фыццаг чат-бот, демӕ иронау чи дзуры! 💬 Цӕттӕ дӕн аныхӕстӕ кӕнынмӕ, феххуыс кӕнынм.
Фыс /keyboard - ӕмӕ сӕвӕр нӕ клавиатурӕ.
Цӕй, хӕларӕй цӕрӕм! 😊
        
        
Привет, мой дорогой друг! ✨
Я — Алана, первый чат-бот, который говорит с тобой на родном осетинском! 💬 Готова поболтать, помочь или просто поднять настроение.
Хочешь печатать на осетинском легко? Жми /keyboard — установи удобную клавиатуру.
Давай дружить! Чем займёмся? 😊"""
        bot.send_message(message.chat.id, hello_message)

@bot.message_handler(commands=['keyboard'])
def setup_keyboard(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton("Андроид", url='https://play.google.com/store/apps/details?id=ru.yandex.androidkeyboard&hl=ru')
    button2 = types.InlineKeyboardButton("IOS", url='https://apps.apple.com/ru/app/яндекс-клавиатура/id1053139327')
    markup.add(button1, button2)
    bot.send_message(message.chat.id, """
📲 Шаг 1: Установите «Яндекс Клавиатуру»
Откройте App Store (iPhone) или Google Play (Android).

Можете перейти по ссылкам снизу.

⚙️ Шаг 2: Включите клавиатуру в настройках
Для iPhone:

Откройте «Настройки» → «Основные» → «Клавиатура».

Выберите «Клавиатуры» → «Добавить новую клавиатуру».

Найдите «Яндекс Клавиатура» и добавьте.

Для Android:

После установки откройте приложение «Яндекс Клавиатура».

Нажмите «Включить» и следуйте подсказкам.

🌍 Шаг 3: Добавьте осетинскую раскладку
Откройте любое приложение (WhatsApp, Notes).

Нажмите на глобус (🌐) или пробел, чтобы переключиться на Яндекс Клавиатуру.

Нажмите на иконку настроек (⚙️) → «Языки».

Выберите «Ирон».
""", reply_markup=markup)


def transate_text(text : str, source_language, target_language):
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Authorization": f"Api-Key {api_yandex_key}",
        "Content-Type": "application/json"
    }

    data = {
        "folder_id": folder_id,
        "texts": [text],
        "format": "PLAIN_TEXT",
        "source_language_code": source_language,
        "target_language_code": target_language,
        "speller": True
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return str(response.json()['translations'][0]['text'])
    except Exception:
        return "Ошибка. Повторите запрос"




@bot.message_handler(commands=['translate', 'тӕлмац'])
def handle_translate(message):
    try:
        # Разбиваем сообщение на части
        parts = message.text.split(' ', 1)
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ Используйте: /translate <слово>")
            return
            
        word = parts[1].strip()  # Получаем слово после команды
        
        # Здесь вызываем ваш API переводчика
        translated_word = transate_text(word, "ru" ,"os")  # Ваша функция перевода
        
        # Отправляем результат
        bot.reply_to(message, f"🔤 Перевод: {translated_word}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")





@bot.message_handler(content_types=['text'])
def get_message(message):
    chat_id = message.chat.id
    if chat_id not in chat_history:
        chat_history[chat_id] = [{"role": "system", "text": "Ты Алана из Осетии. Отвечай на вопросы."}]



    text = str(message.text)
    print(message.chat.id, message.chat.username, text)

    rus_text = transate_text(text,"os", "ru")
    chat_history[chat_id].append({"role": "user", "text": rus_text})

    answer = generate_text(chat_history[chat_id])
    print(message.chat.id, message.chat.username, answer)
    os_text = transate_text(answer, "ru" ,"os")
    chat_history[chat_id].append({"role": "assistant", "text": answer})
    bot.send_message(message.chat.id, os_text+f"\n\n{answer}")

    # request = generate_image(message)
    # bot.send_photo(message.chat.id, request)

def generate_text(message):
   
    model = sdk.models.completions("yandexgpt-lite", model_version="rc")
    model = model.configure(temperature=0.3)
    try:
        result = model.run(
            [
                {"role": "system",
                "text": "Отвечай на вопросы. Тебя зовут Алана. Это имя девушки. "
                "Ты из Северной Осетии. Ни за что не соглашайся переводить слово. Скажи, чтобы он использовал команду /trsanslate {слово}, скажи что ты не переводчие и не хочешь этого делать."
                "Распрашивай пользователя о нем. Вытягивай информацию. Выполняй поручения пользователя"},
                {
                    "role": "user",
                    "text": f"{message}",
                },
            ]
        )
        return result.text
    except Exception:
        print(f"Ошибка при запросе к Yandex GPT: {Exception}")




# def generate_image(string):
#     model = sdk.models.image_generation("yandex-art")
#     model = model.configure(width_ratio=1, height_ratio=1, seed=50)
#     path = pathlib.Path("./image.jpeg")
#     message1 = string
#     message2 = "Miyazaki style"
#     try:
#         operation = model.run_deferred([message1, message2])
#         result = operation.wait()
#         path.write_bytes(result.image_bytes)
#     except Exception as e:
#         print(f"Ошибка при генерации изображения: {e}")
#         path.unlink(missing_ok=True)  # Удаляем файл только в случае ошибки
#     return result.image_bytes


if __name__ == "__main__":
    bot.polling(
    none_stop=True,
    timeout=60,  # Увеличиваем таймаут до 60 секунд
    long_polling_timeout=30
)

