import telebot
from telebot import types
from telebot.util import quick_markup
from config import TOKEN, descriptions, test, counting, results
from extensions import scoring_points, animal_photo

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    username = message.chat.first_name if message.chat.first_name else "друг"

    photo = open('./photo/MosZoo_main_entrance.jpg', 'rb')
    bot.send_photo(
        message.chat.id,
        photo,
        caption=(
            f'Здравствуй, {username}! Вас приветствует Московский зоопарк — один из старейших зоопарков Европы.\n'
            'Мы предлагаем Вам принять участие в программе «Клуб друзей зоопарка» — это помощь в содержании наших '
            'обитателей, а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка.\n'
            'Традиция опекать животных в Московском зоопарке возникла с момента его создания в 1864г. '
            'Такая практика есть и в других зоопарках по всему миру.\n Вы можете взять под крыло любого обитателя у '
            'нас. Сделать это очень просто!: \n •  Выберите животное, которое Вы хотели бы опекать \n'
            ' •  Определите сумму пожертвования \n •  Затем мы с Вами согласуем договор \n •  Готово! Ждем Вас в гости,'
            'чтобы подписать договор и \n'
            '    передать Вам Вашу карту опекуна.\n'
            'Если же Вы затрудняетесь с выбором подопечного, предлагаем пройти тест "Кто Вы в мире животных", '
            'который в этом поможет. Итак, нажмите: /goTest'
        )
    )
    photo.close()


@bot.message_handler(commands=['goTest'])
def start_test(message):
    user_id = message.chat.id
    if user_id not in counting:
        counting[user_id] = {'current_question': 0, 'answers': []}

    incoming_questions(user_id)


def incoming_questions(user_id):
    user = counting.get(user_id)
    if not user:
        bot.send_message(user_id, "Пройдите викторину.")
        return

    number_questions = user['current_question']
    try:
        if number_questions < len(test):
            question_list = test[number_questions]
            question = question_list['question']
            answers = question_list['answer']

            markup = types.InlineKeyboardMarkup()
            for answer in answers.keys():
                markup.add(types.InlineKeyboardButton(text=answer, callback_data=f'{number_questions}_{answer}'))
                print('number_questions: ', number_questions)
                print('answer: ', answer)
            bot.send_message(user_id, question, reply_markup=markup)
        else:
            print('user["answers"]: ', user['answers'])
            results[user_id] = scoring_points(user['answers'])
            animal = scoring_points(user['answers'])

            description = ''
            if animal == 'Кошка':
                description = descriptions[0]
            elif animal == 'Лиса':
                description = descriptions[1]
            elif animal == 'Волк':
                description = descriptions[2]
            elif animal == 'Медведь':
                description = descriptions[3]

            photo = open(animal_photo(animal), 'rb')

            markup_end = types.InlineKeyboardMarkup()
            markup_end.add(types.InlineKeyboardButton(text='Подробнее о Программе опеки на сайте Московского зоопарка',
                                                      url='https://moscowzoo.ru/about/guardianship'))
            markup_end.add(types.InlineKeyboardButton(text='Задать вопрос сотруднику Зоопарка',
                                                      callback_data='question'))
            markup_end.add(types.InlineKeyboardButton(text='Перезапустить тест', callback_data='replay'))
            markup_end.add(types.InlineKeyboardButton(text='Поделиться результатом в соцсетях', callback_data='inform'))
            markup_end.add(types.InlineKeyboardButton(text='Отправить отзыв', callback_data='survey'))

            bot.send_photo(user_id, photo, caption=(
                f'Итак, в мире животных Вы - {animal}! '
                f'{description}\n'
                f'В нашем зоопарке как раз есть животное близкое Вам по духу, которое ждет вашей опеки.'
            ), reply_markup=markup_end)
            photo.close()

    except Exception as e:
        bot.send_message(user_id, "Произошла ошибка. Пожалуйста, попробуйте снова.")
        print(f"Error: {e}")
        counting[user_id]['current_question'] = 0
        counting[user_id]['answers'] = []


@bot.callback_query_handler(func=lambda call: '_' in call.data)
def callback_query(call):
    user_id = call.message.chat.id
    user = counting[user_id]

    number_questions, user_answer = call.data.split('_')
    number_questions = int(number_questions)

    user['answers'].append(user_answer)
    user['current_question'] = number_questions + 1
    print('callback_query: ', counting)
    incoming_questions(user_id)


@bot.callback_query_handler(func=lambda call: call.data in ['replay', 'survey', 'question', 'inform'])
def handle_special_buttons(call):
    user_id = call.message.chat.id
    if call.data == 'replay':
        if user_id in counting:
            del results[user_id]
            counting[user_id]['current_question'] = 0
            counting[user_id]['answers'] = []
            incoming_questions(user_id)
        else:
            bot.send_message(user_id, "Тест невозможно перезапустить. Нажмите /goTest")

    elif call.data == 'survey':
        bot.send_message(user_id, "Написать отзыв по e-mail: [zoofriends@moscowzoo.ru](e-mail:zoofriends@moscowzoo.ru)",
                         parse_mode='Markdown')

    elif call.data == 'question':
        bot.send_message(user_id, "Позвонить по телефону: [+79991234567](tel:+79991234567)", parse_mode='Markdown')
        bot.send_message(user_id, "Написать по e-mail: [zoofriends@moscowzoo.ru](e-mail:zoofriends@moscowzoo.ru)",
                         parse_mode='Markdown')

    elif call.data == 'inform':
        markup_soc = quick_markup({
            'ВКонтакте': {'url': 'https://vk.com'},
            'Одноклассника': {'url': 'https://ok.com'},
            'Zen': {'url': 'https://zen.yandex.ru'},
            'LiveJournal': {'url': 'https://www.livejournal.com'}

        }, row_width=2)
        bot.send_message(user_id, "Выберите соцсеть:", reply_markup=markup_soc)

    bot.answer_callback_query(call.id)


bot.polling(none_stop=True)
