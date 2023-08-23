import logging
import json
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ChatActions
import os
import time
import uuid
from os import getenv
from sys import exit
import asyncio
import speech_recognition as sr
    
bot_token = "304461941:AAEXOyzq8sl3CSOOTjFm80mh3ATDdC1xcRg"#getenv("BOT_TOKEN")
if not bot_token: exit("Error: no token provided")
    
logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
#=========================поднимает файл с диска и отправляет в чат =======


def SelectOpenFileDialog():
    return ""
    
@dp.message_handler(regexp='(^tts|speak|talk|/tts|/speak|/talk)')
async def send_tts_from_local_disk(message: types.Message):
    import pyttsx3
    import uuid
    with open(SelectOpenFileDialog(), 'r') as new_file:
        what_to_say=new_file.read()                    

    tts = pyttsx3.init()
    voices = tts.getProperty('voices')
    # Задать голос по умолчанию
    tts.setProperty('voice', 'ru') 
    # Попробовать установить предпочтительный голос
    for voice in voices:
        if voice.name == 'Evgeniy-Rus':
            tts.setProperty('voice', voice.id)
    unique_number=uuid.uuid4()        
    tts.save_to_file(what_to_say, r"V:\\"+str(unique_number)+".mp3")
    tts.runAndWait()
    print("Have spoken TTS to file <= " +str(unique_number)+".mp3")
    await message.answer_chat_action(action = 'upload_document')
    with open(r"V:\\"+str(unique_number)+".mp3", 'rb') as document:
        await message.reply_document(document)
#=========================поднимает файл с диска, проговаривает и отправляет в чат =======                
 
# States
class Slots(StatesGroup):
    selfie = State(state= "твое последнее селфи b фото из старшей школы")
    hobby = State(state= "пост о твоём главном увлечении")  
    voice = State(state= "войс о GPT & войс о SQL-NoSQL & войс История первой любви")  
    source = State(state= "получить ссылку на репозиторий ")
    stopped = State(state= "Бот остановлен.")   

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Slots.selfie.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["твое последнее селфи","фото из старшей школы"]
    keyboard.add(*buttons)
    await message.answer("Привет, я бот тестового задания. Готов выбрать вариант фото?", reply_markup=keyboard)

# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
@dp.message_handler(Text(equals='стоп', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state ')
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.answer('Бот остановлен. Переписка завершена. Для перезапуска введите /start', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text  in ["твое последнее селфи"],state=Slots.selfie)
async def call_routine_to_process_selfie(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not 'selfie' in data.keys():
            data['selfie'] = 0
        if data['selfie'] >=2 :
            await Slots.next()
            await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
            await asyncio.sleep(3)                        
            await message.answer('Хочешь читать пост о моём главном увлечении? Напиши *да* или *нет*',parse_mode=ParseMode.MARKDOWN, reply_markup=types.ReplyKeyboardRemove())
        else:
            data['selfie'] +=1
            with open("2a496c22-bee8-4248-b38f-e0ccb05b88f3.jpg", 'rb') as document:
                await message.reply_document(document)

@dp.message_handler(lambda message: message.text  in ["фото из старшей школы"], state=Slots.selfie)
async def call_routine_to_process_oldphoto(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not 'selfie' in data.keys():
            data['selfie'] = 0        
        if data['selfie'] >=2 :
            await Slots.next()
            await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
            await asyncio.sleep(3)            
            await message.answer('Хочешь читать пост о моём главном увлечении? Напиши *да* или *нет*', parse_mode=ParseMode.MARKDOWN, reply_markup=types.ReplyKeyboardRemove())
        else:
            data['selfie'] +=1
            with open("64a57a20-23ca-468f-8c81-14e0f6c2dfbd.jpg", 'rb') as document:
                await message.reply_document(document)            


@dp.message_handler(lambda message: message.text  in ["да","Да"], state=Slots.hobby)
async def call_routine_to_process_hobby_yes(message: types.Message, state: FSMContext):
    await Slots.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["войс о GPT","войс о SQL-NoSQL","войс История первой любви"]
    keyboard.add(*buttons)
    await message.answer("""Программирование – это увлечение, которому я отдаю свободное время и которое доставляет удовольствие.

Хобби программистов могут отличаться по тематике, сложности и стилю.

Важно выбрать язык программирования, который подходит именно Вам и помогает развиваться как личности.

И я готов Вам в этом помогать.""", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(3)
    await message.answer("""Хочешь послушать голосовые сообщения?""", reply_markup=keyboard)
    
@dp.message_handler(lambda message: message.text  in ["нет","Нет"], state=Slots.hobby)
async def call_routine_to_process_hobby_no(message: types.Message, state: FSMContext):
    await Slots.source.set()
    await message.answer("В завершение нашей переписки отправляю ссылку на репозиторий")
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(3)
    await message.answer("""[https://github.com/Ucharacters/Yandex-task](https://github.com/Ucharacters/Yandex-task)""",parse_mode=ParseMode.MARKDOWN, reply_markup=types.ReplyKeyboardRemove())
    logging.info('Cancelling state')
    await state.finish()
    
@dp.message_handler(lambda message: message.text  in ["войс о GPT"],state=Slots.voice)
async def call_routine_to_process_voice_gpt(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not 'voice' in data.keys():
            data['voice'] = 0        
        if data['voice'] >=3:
            await message.answer("войс о GPT?")
        else:
            data['voice'] +=1
            with open("0361b32b-19f5-4145-a5a5-bc8dea7d8d87.ogg", 'rb') as document:
                await message.reply_document(document)                     
    
@dp.message_handler(lambda message: message.text  in ["войс о SQL-NoSQL"],state=Slots.voice)
async def call_routine_to_process_voice_SQL_NoSQL(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not 'voice' in data.keys():
            data['voice'] = 0        
        if data['voice'] >=3:
            await message.answer("войс о SQL-NoSQL?")
        else:
            data['voice'] +=1
            with open("bbe9aecb-b8a5-4765-808c-e9f5585973a9.ogg", 'rb') as document:
                await message.reply_document(document)
                

@dp.message_handler(lambda message: message.text  in ["войс История первой любви"],state=Slots.voice)
async def call_routine_to_process_voice_SQL_love(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not 'voice' in data.keys():
            data['voice'] = 0        
        if data['voice'] >=3:
            await message.answer("войс История первой любви?")
        else:
            data['voice'] +=1
            with open("43bfefef-10c9-458f-88a4-48bccb71982e.ogg", 'rb') as document:
                await message.reply_document(document)    


@dp.message_handler(regexp='(^git|/git)')
@dp.message_handler(state='*', commands='git')
@dp.message_handler(state=Slots.source)
async def call_routine_to_process_source(message: types.Message, state: FSMContext):
    await message.answer("""[https://github.com/Ucharacters/Yandex-task](https://github.com/Ucharacters/Yandex-task)""",parse_mode=ParseMode.MARKDOWN, reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Slots.stopped)
async def call_routine_to_process_stopped(message: types.Message, state: FSMContext):
    await message.answer('Бот остановлен. Переписка завершена. Для перезапуска введите /start', reply_markup=types.ReplyKeyboardRemove())

#========================= Задача со звездочкой Сможет ли твой бот принимать от нас голосовые команды=======
   
@dp.message_handler(content_types=[types.ContentType.VOICE])
async def download_any_voice(message: types.Message):
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        await message.voice.download(destination=dir_path+"/64a57a20-23ca-468f-8c81-.ogg")

        harvard = sr.AudioFile(dir_path+"/64a57a20-23ca-468f-8c81-.ogg")
        r = sr.Recognizer ()
        with harvard as source:
            audio = r.record(source)
        await message.answer("Вы сказали :"+r.recognize_google(audio,language='ru-RU')) 
    except:
        logging.info('download_any_voice ')
        pass
    
@dp.message_handler(content_types=[types.ContentType.AUDIO])
async def download_any_audio(message: types.Message):
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        await message.voice.download(destination=dir_path+"/64a57a20-23ca-468f-8c81-.wav")

        harvard = sr.AudioFile(dir_path+"/64a57a20-23ca-468f-8c81-.wav")
        r = sr.Recognizer ()
        with harvard as source:
            audio = r.record(source)
        await message.answer("Вы сказали :"+r.recognize_google(audio,language='ru-RU'))
    except:
        logging.info('download_any_audio')
        pass

#========================= Задача со звездочкой Сможет ли твой бот принимать от нас голосовые команды=======    


    
if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except NetworkError:
        print("except NetworkError")
        time.sleep(30)
        pass
