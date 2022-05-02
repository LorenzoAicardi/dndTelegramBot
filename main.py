import logging
import os
from dotenv import load_dotenv
from telegram.ext import Updater, PicklePersistence
from classes import menu

load_dotenv()
TOKEN = os.getenv('TOKEN')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
cwd = os.getcwd()


def main():
    # persistence = PicklePersistence(filename=os.path.join(cwd, "data/bot_data.txt"))
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(menu.start_cmd())

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
