import os
import random
from ultralytics import YOLO
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import json

with open('F:/pet projects/ImageQuizBot/results_dict.json', 'r') as file:
    data_dict = json.load(file)

TOKEN = '6634137306:AAEPTFYi9JlkExW1gfiVGOi9NAmlUdE-ADY'
BOT_USERNAME = '@image_quiz_bot'

names = {0: 'ellipse', 1: 'other', 2: 'rectangle', 3: 'triangle'}

IMAGES_FOLDER = 'F:/pet projects/ImageQuizBot/data_new/val'

model = YOLO('F:/pet projects/ImageQuizBot/runs/classify/train11/weights/best.pt')

user_scores = {}
model_scores = {}
user_preds = {}

ASK_QUESTION, ANSWER, REQUEST_PHOTO, PREDICTION, CHOOSING_ACTION = range(5)

def predict_class(image_path):
    probs = model([image_path])[0].probs
    top4 = probs.top5
    classes = [names[i] for i in top4]
    probs4 = probs.top5conf.tolist()
    output = (classes[0] + ' - ' + str(round(probs4[0],2)) + '\n')
    for i in range(1,4):
        output += (classes[i] + ' - ' + str(round(probs4[i],2)) + '\n')
    return output

def get_random_image(image_dir):
    folders = os.listdir(image_dir)
    folder = random.choice(folders)
    files = os.listdir(os.path.join(image_dir, folder))
    file = random.choice(files)
    path = os.path.join(image_dir, folder, file)
    return file, folder, path

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("In this game, the AI model is a pre-trained YOLOv8 nano image classifier. It was fine-tuned on similar images but has never seen the specific images that will be used in the game. You can expect high accuracy from the model due to its state-of-the-art design.\n\nIn the future, this bot may be updated to include more various and complex kinds of games. Feel free to reach out if you have any questions or ideas regarding this bot. I'm open to suggestions and feedback:)\n\ndeveloper - @funee_monkee")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'{update.effective_user.full_name} in start')
    user_id = update.effective_user.id
    user_scores[user_id] = 0
    model_scores[user_id] = 0
    reply_keyboard = [["Play","Predict figure"]]
    await update.message.reply_text("Hi! Press 'Play' if you are ready to play!\nPress 'Predict figure' if you want to test AI's perfomance on your own.", reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return CHOOSING_ACTION

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'{update.effective_user.full_name} in ask_question')
    image_file, correct_answer, path = get_random_image(IMAGES_FOLDER)

    context.user_data['correct_answer'] = correct_answer
    context.user_data['file_path'] = path

    keyboard = [['Ellipse', 'Rectangle', 'Triangle', 'Other'],['Exit']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                        one_time_keyboard=True, input_field_placeholder="What's in the picture?")

    await update.message.reply_photo(photo=open(path, 'rb'), reply_markup=reply_markup)
    return ANSWER


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'{update.effective_user.full_name}in get_answer')
    user_id = update.effective_user.id
    
    user_answer = update.message.text.lower()
    correct_answer = str(context.user_data.get('correct_answer'))

    model_answer = data_dict[str(context.user_data.get('file_path'))]

    if user_answer == correct_answer:
        user_scores[user_id] += 1

    if model_answer == correct_answer:
        model_scores[user_id] += 1
        
    if user_scores[user_id] < 10 and model_scores[user_id] < 10:
        await update.message.reply_text(f"Your answer: {user_answer}\nModel's answer: {model_answer}\nCorrect answer: {correct_answer}\n\nYou    Model\n{user_scores[user_id]}         {model_scores[user_id]}")

    if user_scores[user_id] >= 10 or model_scores[user_id] >= 10:
        reply_keyboard = [["Play again", "Exit"]]
        if user_scores[user_id] > model_scores[user_id]:
            result_message = "You win! People still can do something!"
        elif user_scores[user_id] == model_scores[user_id]:
            result_message = "Draw! You are worthy opponent!"
        else:
            result_message = "You lose! It seems that artificial intelligence will soon destroy humanity..."
        result_message += f"\nYour score: {user_scores[user_id]}\n"
        result_message += f"AI's score: {model_scores[user_id]}"
        await update.message.reply_text(result_message, reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                          resize_keyboard=True, one_time_keyboard=True))

        user_scores[user_id] = 0
        model_scores[user_id] = 0

        return ASK_QUESTION

    return await ask_question(update, context)

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'{update.effective_user.full_name} in end')
    user_id = update.effective_user.id
    user_scores.pop(user_id)
    model_scores.pop(user_id)
    await update.message.reply_text('Thank you. To play again send /start. Bye!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def request_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Send figure picture to classify")
    return PREDICTION

async def prediction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'{update.effective_user.full_name} in prediction')
    user_id = update.effective_user.id
    reply_keyboard = [['Another photo', 'Exit']]
    photo_file = await update.message.photo[-1].get_file()
    path = f"F:/pet projects/ImageQuizBot/user_image/{update.effective_user.full_name}_photo.jpg"
    await photo_file.download_to_drive(path)
    await update.message.reply_text(f"AI's predicted probabilities: \n {predict_class(path)}", reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                                          resize_keyboard=True, one_time_keyboard=True))
    #os.remove(path)

    return REQUEST_PHOTO


async def choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'{update.effective_user.full_name} in choosing')
    user_text = update.message.text
    if user_text == 'Play':
        return await ask_question(update, context)
    elif user_text == 'Predict figure':
        return await request_photo(update, context)



def main() -> None:
    print('Starting bot...')
    application = Application.builder().token(TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_QUESTION: [MessageHandler((filters.TEXT | filters.Regex("^Play again$") ) & ~(filters.COMMAND | filters.Regex("^Exit$")), ask_question)],
            ANSWER: [MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Exit$")), get_answer)],
            CHOOSING_ACTION: [MessageHandler((filters.TEXT | filters.Regex("^Play again$") ) & ~(filters.COMMAND | filters.Regex("^Exit$")), choosing)],
            REQUEST_PHOTO: [MessageHandler((filters.TEXT | filters.Regex("^Another photo$") | filters.Regex("^Predict figure$")) & ~(filters.COMMAND | filters.Regex("^Exit$")), request_photo)],
            PREDICTION: [MessageHandler(filters.PHOTO, prediction)],

        },
        fallbacks=[MessageHandler(filters.Regex("^Exit$"), end)],
    )
    
    application.add_handler(CommandHandler('info', info_command))
    application.add_handler(conversation_handler)
    

    print('Polling...')
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
