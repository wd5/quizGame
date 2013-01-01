import MySQLdb
from questions import Topic
from quiz_globals import QUESTIONS_CACHE_SIZE



_connection = MySQLdb.connect(host='127.0.0.1', user='chgk_user', passwd='password', db='questions', charset='utf8')
_cursor = _connection.cursor()

def _load_questions():
    global cursor_iter
    _cursor.execute(
        'SELECT Question, Answer FROM questions.Questions WHERE TypeNum = 5 ORDER BY RAND() LIMIT %s' % QUESTIONS_CACHE_SIZE)
    cursor_iter = iter(_cursor.fetchone, None)

_load_questions()

def get_topic():
    """
    :rtype : Topic
    """
    while True:
        try:
            topic_data = next(cursor_iter)
        except StopIteration:
            _load_questions()
            topic_data = next(cursor_iter)

        yield Topic(topic_data)

def get_question_iter():
    while True:
        topic = next(get_topic())

        for i, question in enumerate(topic.questions):
            yield (topic.topic_name, question, topic.answers[i], (i + 1) * 10)

question_iter = get_question_iter()