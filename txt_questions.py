import io
import re


def get_questions(path):
    with io.open(path, mode='r', encoding='koi8-r') as file:
        file_str = file.read()
        blank_line_regex = r'(?:\r?\n){2,}'
        questions = re.split(blank_line_regex, file_str.strip())

    no_title_info = questions[2:]
    questions_dict = []
    for i in range(0, len(no_title_info), 4):
        questions_dict.append({
            'question':  no_title_info[i].split(':')[1],
            'answer': no_title_info[i+1].split(':')[1],
            'comment': no_title_info[i+2].split(':')[1],
            'author': no_title_info[i+3].split(':')[1],
        })
    return questions_dict


if __name__ == '__main__':
    zz = get_questions('questions\\osel95.txt')
