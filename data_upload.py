import os
import argparse
import redis
import logging

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def main():
    load_dotenv()
    storage = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        password=os.environ.get('REDIS_PASSWORD', default=''),
        db=os.environ.get('REDIS_DB', default=0))
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    parser = argparse.ArgumentParser(description='Загрузка вопросов для ВИКТОРИНЫ')
    parser.add_argument(
        '--file',
        nargs='*',
        default=['questions.txt'],
        help='имя файла с вопросами для викторины '
    )

    try:
        with open(os.path.join(os.getcwd(), parser.parse_args().file[0]), "r", encoding="KOI8-R") as questions:
            file_contents = questions.read()
    except (FileNotFoundError, ValueError) as error:
        logger.info(f'Неверно указан путь к файлу.\n Ошибка: {error}')
        exit()
    separated_contents = file_contents.split('\n\n')
    questions = {}
    question = ''
    for content in separated_contents:
        if 'Вопрос ' in content:
            question = content[content.find(':') + 2:].replace('\n', ' ')
        elif 'Ответ:' in content:
            answer = content[content.find(':') + 2:].replace('\n', ' ')
            questions[question] = answer
    storage.hset(name='questions', mapping=questions)
    questions.clear()


if __name__ == '__main__':
    main()
