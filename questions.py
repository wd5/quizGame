import re

class Topic():

    def __init__(self, source):

        def parse_string_from_db(string):
            return [entry.replace('\n', ' ') for entry
                    in re.split('(?m)^\s*\d+\.\s', string) if entry]

        questions_source = source[0]
        title_end = questions_source.find('\n')
        self.topic_name = questions_source[:title_end]

        self.questions = parse_string_from_db(questions_source[title_end:])

        answer_source = source[1]
        self.answers = parse_string_from_db(answer_source)