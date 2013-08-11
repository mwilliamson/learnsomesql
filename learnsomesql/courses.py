import re
from xml.dom import minidom

from xmlfilter import filter_xml


class CourseReader(object):
    def __init__(self, executor):
        self._executor = executor
    
    def read_file(self, f, dialect):
        document = filter_xml(minidom.parse(f), dialect)
        course_element = document.documentElement
        creation_sql = self._read_creation_sql(course_element)
        lessons_reader = LessonsReader(self._executor, creation_sql)
        lessons = lessons_reader.read_lessons(course_element)
        return Course(creation_sql, lessons)

    def _read_creation_sql(self, course_element):
        creation_sql_element = _find(course_element, "creation-sql")
        if creation_sql_element is None:
            return []
        else:
            return [
                command
                for command in re.split(r"\s*\n\s*\n\s*", _text(creation_sql_element).strip())
            ]


class LessonsReader(object):
    def __init__(self, executor, creation_sql):
        self._executor = executor
        self._creation_sql = creation_sql
        
    def read_lessons(self, course_element):
        lessons_element = _find(course_element, "lessons")
        return map(
            self._read_lesson_element,
            _find_elements(lessons_element, "lesson"),
        )
            
    def _read_lesson_element(self, lesson_element):
        slug = _text(_find(lesson_element, "slug"))
        title = _text(_find(lesson_element, "title"))
        description = _inner_xml(_find(lesson_element, "description"))
        
        questions_element = _find(lesson_element, "questions")
        questions = map(
            self._read_question_element,
            _find_elements(questions_element, "question"),
        )
        
        return Lesson(
            slug=slug,
            title=title,
            description=description,
            questions=questions,
        )
        
    def _read_question_element(self, question_element):
        description = _inner_xml(_find(question_element, "description"))
        correct_query = _text(_find(question_element, "correct-query"))
        expected_results = self._execute(correct_query).table
        
        return Question(
            description=description,
            correct_query=correct_query,
            expected_results=expected_results,
        )
        
    def _execute(self, sql):
        return self._executor.execute(self._creation_sql, sql)
        

def _find(node, name):
    for child in node.childNodes:
        if child.nodeType == child.ELEMENT_NODE and child.tagName == name:
            return child


def _find_elements(node, name):
    if node is None:
        return []
        
    def _is_element(node):
        return node.nodeType == node.ELEMENT_NODE and node.tagName == name
    
    return filter(_is_element, node.childNodes)


def _text(node):
    if node is None:
        return ""
    elif node.nodeType == node.TEXT_NODE:
        return node.nodeValue
    else:
        return "".join(map(_text, node.childNodes))


def _inner_xml(node):
    if node is None:
        return ""
    else:
        return "".join(child.toxml() for child in node.childNodes).strip()


class Course(object):
    def __init__(self, creation_sql, lessons):
        self.creation_sql = creation_sql
        self.lessons = lessons


class Lesson(object):
    def __init__(self, slug, title, description, questions):
        self.slug = slug
        self.title = title
        self.description = description
        self.questions = questions


class Question(object):
    def __init__(self, description, correct_query, expected_results):
        self.description = description
        self.correct_query = correct_query
        self.expected_results = expected_results
