import logging
import os
from dotenv import load_dotenv
from telegram.ext import Updater
from bot import startMenu, charCreationMenu, dmMenu

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
cwd = os.getcwd()


def main():
    # persistence = PicklePersistence(filename=os.path.join(cwd, "data/bot_data.txt"))
    updater = Updater(os.getenv('TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(startMenu.start_cmd())
    dispatcher.add_handler(charCreationMenu.createChar())
    dispatcher.add_handler(dmMenu.activeCamp())

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
