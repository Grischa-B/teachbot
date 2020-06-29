import logging
import datetime
from math import sqrt
from tinydb import TinyDB, Query
from random import randrange
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
						  ConversationHandler, Defaults)
import os
import yaml
PORT = int(os.environ.get('PORT', 5000))
TOKEN = ''
HOST_URL = ''
ADMIN_ID = 0

# fin = open("days.yml", 'r')
common_data = yaml.load(open("days.yml", 'r'))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)
# users = {}
INFO, QUESTION = range(2)
db = TinyDB('db.json')
query = Query()

GREETINGS = ('Hello 👋 ','Hi 👋 ','Let’s learn English🇬🇧','I’m ready 🤟','👋👋👋','Let’s start🤟📚')
CORRECT = ('Good! ✅','Well done 👍✅','Correct ✅','Right👌✅','The answer is correct 👏✅')
INCORRECT = ('Wrong. Try again ❌','Try again 🙅‍♀️','Not correct. Try again ❌','Sorry, no. Try again🙅‍♂️','Oops.. incorrect. Try again ❌') 

def list_to_matrix(arr):
	m=[]
	s=round(sqrt(len(arr)))
	while arr != []:
		m.append(arr[:s])
		arr=arr[s:]
	return m

def hallo(context):
	context.bot.send_message(context.job.context, text='Guten Tag!')


def start(update, context):
	db.insert({'id':update.message.from_user.id,
			   'score':0,
			   'day':1,
			   'progress':0,
			   'wrong_ans':0,
			   })
	# users[update.message.from_user.id] = USER()
	update.message.reply_text(
		common_data['day_1']['text']['intro'],
		reply_markup=ReplyKeyboardMarkup([[GREETINGS[randrange(len(GREETINGS))]]],
														resize_keyboard=True,
														one_time_keyboard=False))
	# context.chat_data['job'] = context.job_queue.run_daily(callback=hallo,
	# 													   time=datetime.time(hour=9, minute=3),
	# 													   context=update.message.chat_id)
	return QUESTION


def question(update, context):
	user = update.message.from_user
	cur_progress = db.search(query.id == user.id)[0]['progress']
	day = db.search(query.id == user.id)[0]['day']
	#Checking answer to the past question
	if cur_progress > 0:
		# wrong_ans=0
	# if users[user.id].get_progress() > 0:
		past_task = common_data['day_'+str(day)]['questions'][0]['group'][cur_progress -1]['question']
		# past_task = common_data['day_'+str(day)]['questions'][0]['group'][users[user.id].get_progress()-1]['question']
		if past_task['type'] == 'buttons' or past_task['type'] == 'manual':
			if update.message.text.lower() in [x.lower() for x in past_task['corr_answer']]:
				update.message.reply_text(CORRECT[randrange(len(CORRECT))])
				db.update({'score':db.search(query.id == user.id)[0]['score']+1}, query.id == user.id)
				db.update({'wrong_ans':0}, query.id == user.id)
			else:
				update.message.reply_text(INCORRECT[randrange(len(INCORRECT))])
				cur_progress-=1
				db.update({'wrong_ans':db.search(query.id == user.id)[0]['wrong_ans']+1}, query.id == user.id)
				# wrong_ans+=1
				if db.search(query.id == user.id)[0]['wrong_ans'] == 2:
					update.message.reply_text('Correct answers are below.',
												reply_markup=ReplyKeyboardMarkup(list_to_matrix(past_task['corr_answer']),
										       										one_time_keyboard=False,
																					resize_keyboard=True))
					db.update({'wrong_ans':0}, query.id == user.id)
					# wrong_ans = 0
				return QUESTION
		elif past_task['type'] == 'number':
			tmp=''
			for i in update.message.text:
				if i.isdigit():
					tmp+=i
			if tmp in past_task['corr_answer']:
				update.message.reply_text(CORRECT[randrange(len(CORRECT))])
				db.update({'score':db.search(query.id == user.id)[0]['score']+1}, query.id == user.id)
				db.update({'wrong_ans':0}, query.id == user.id)
			else:
				update.message.reply_text(INCORRECT[randrange(len(INCORRECT))])
				cur_progress-=1
				# wrong_ans+=1
				db.update({'wrong_ans':db.search(query.id == user.id)[0]['wrong_ans']+1}, query.id == user.id)
				if db.search(query.id == user.id)[0]['wrong_ans'] == 2:
					update.message.reply_text('Correct answers are below.',
												reply_markup=ReplyKeyboardMarkup(list_to_matrix(past_task['corr_answer']),
										       										one_time_keyboard=False,
				 																	resize_keyboard=True,))
				return QUESTION
		elif past_task['type'] == 'user':
			context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user.id, message_id=update.message.message_id)

	if cur_progress < len(common_data['day_'+str(day)]['questions'][0]['group']):
	# if users[user.id].progress < len(common_data['day_'+str(day)]['questions'][0]['group']):
		task = common_data['day_'+str(day)]['questions'][0]['group'][cur_progress]['question']
		# task = common_data['day_'+str(day)]['questions'][0]['group'][users[user.id].get_progress()]['question']

	# if cur_progress < len(common_data['day_'+str(day)]['questions'][0]['group']):
	# if users[user.id].progress < len(common_data['day_'+str(day)]['questions'][0]['group']):

	#Asking new question
		if task['type'] == 'buttons':
			if 'meta' in task:
				if task['meta']['type'] == 'image':
					update.message.reply_photo(photo=open('./images/'+task['meta']['path'], 'rb'),
											   caption=task['value'],
							                   reply_markup=ReplyKeyboardMarkup(list_to_matrix(task['variations']),
														resize_keyboard=True,
										       		one_time_keyboard=False))
				elif task['meta']['type'] == 'audio':
					update.message.reply_audio(audio=open('./audio/'+task['meta']['path'], 'rb'),
											   caption=task['value'],
							                   reply_markup=ReplyKeyboardMarkup(list_to_matrix(task['variations']),
														resize_keyboard=True,
										       		one_time_keyboard=False))
			else:
			# reply_keyboard = task['variations']
				update.message.reply_text(task['value'],
								reply_markup=ReplyKeyboardMarkup(list_to_matrix(task['variations']),
														resize_keyboard=True,
											one_time_keyboard=False))
		elif task['type'] == 'manual' or task['type'] == 'user' or task['type'] == 'info' or task['type'] == 'number':
			if 'meta' in task:
				if task['type'] == 'info':
					if task['meta']['type'] == 'image':
						update.message.reply_photo(photo=open('./images/'+task['meta']['path'], 'rb'),
												   caption=task['value'],
												   reply_markup=ReplyKeyboardMarkup([['Okay!']],
														resize_keyboard=True,
												   		one_time_keyboard=False))
					elif task['meta']['type'] == 'audio':
						update.message.reply_audio(audio=open('./audio/'+task['meta']['path'], 'rb'),
												   caption=task['value'],
                                                  reply_markup=ReplyKeyboardMarkup([['Okay!']],
														resize_keyboard=True,
												   		one_time_keyboard=False))
					elif task['meta']['type'] == 'pdf':
						update.message.reply_document(document=open('./pdf/'+task['meta']['path'], 'rb'),
												   caption=task['value'],
												   reply_markup=ReplyKeyboardMarkup([['Okay!']],
														resize_keyboard=True,
												   		one_time_keyboard=False))
				else:
					if task['meta']['type'] == 'image':
						update.message.reply_photo(photo=open('./images/'+task['meta']['path'], 'rb'),
												   caption=task['value'])
					elif task['meta']['type'] == 'audio':
						update.message.reply_audio(audio=open('./audio/'+task['meta']['path'], 'rb'),
												   caption=task['value'])
			else:
				if task['type'] == 'info':
					update.message.reply_text(task['value'],
										reply_markup=ReplyKeyboardMarkup([['Okay!']],
											resize_keyboard=True,
											one_time_keyboard=False))
				else:
					update.message.reply_text(task['value'],
										reply_markup=ReplyKeyboardRemove())

	db.update({'progress':cur_progress+1}, query.id==user.id)
	# users[user.id].inc_progress()

	if cur_progress == len(common_data['day_'+str(day)]['questions'][0]['group']):
	# if users[user.id].get_progress() == 1+len(common_data['day_'+str(day)]['questions'][0]['group']):
		db.update({'wrong_ans':0}, query.id == user.id)
		update.message.reply_text(common_data['day_'+str(day)]['text']['outro'],
								  reply_markup=ReplyKeyboardMarkup([['Bye!!']],
														resize_keyboard=True,
								  		one_time_keyboard=False))
		if day == 31:
			return ConversationHandler.END
		else:
			db.update({'day':day+1}, query.id == user.id)
			db.update({'progress':0}, query.id == user.id)
			return QUESTION
	else:
		return QUESTION


def cancel(update, context):
	user = update.mfallessage.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('Bye! I hope we can talk again some day.',
							  reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END


def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)
	context.bot.send_message(chat_id=ADMIN_ID, text='Update '+update+' caused error '+context.error)

def main():
	updater = Updater(TOKEN,
					  use_context=True,
					  defaults=Defaults(parse_mode=ParseMode.HTML))
	dp = updater.dispatcher

	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start, pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True)],

		states={
			QUESTION: [MessageHandler(Filters.text, question)],
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_webhook(listen="0.0.0.0",
						  port=int(PORT),
						  url_path=TOKEN)
	updater.bot.setWebhook(HOST_URL + TOKEN)

	updater.idle()


if __name__ == '__main__':
	main()