import telebot
from utils import *
from telebot import types

bot = telebot.TeleBot(os.environ.get('token'))
pattern = 'Word: {1}\nAccent: {0}'


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def handle(query):
    args = query.query.split()
    if len(args) == 2 and args[0] in accents:
        bot.answer_inline_query(query.id, form_response(*args), cache_time=0)
    track_action(query.from_user.id, query.query)


def form_response(accent, word):
    response = []
    for i, j in enumerate(search(word), 1):
        url = get_audio(j, accent)
        if url:
            inline_response = types.InlineQueryResultVoice(
                voice_url=url['audio'], title=j, id=i,
                reply_markup=get_keyboard(url),
                caption=pattern.format(accents[accent]['name'], j)
            )
            response.append(inline_response)
    return response


def get_keyboard(url):
    examples = url['examples']
    markup = types.InlineKeyboardMarkup()
    if examples:
        markup.add(types.InlineKeyboardButton(text='Examples', url=examples))
    return markup


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=100000)
