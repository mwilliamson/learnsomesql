import re
from xml.dom import minidom

from xmlfilter import filter_xml


class CourseReader():
    def __init__(self, executor):
        self._executor = executor
    
    def read_file(self, f, dialect):
        document = filter_xml(minidom.parse(f), dialect)
        course_element = document.documentElement
        creation_sql = self._read_creation_sql(course_element)
        return Course(creation_sql, [])
        
    def _read_creation_sql(self, course_element):
        creation_sql_element = self._find(course_element, "creation-sql")
        if creation_sql_element is None:
            return []
        else:
            return [
                command
                for command in re.split(r"\s*\n\s*\n\s*", self._text(creation_sql_element).strip())
            ]

    def _find(self, node, name):
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE and child.tagName == name:
                return child
                
    def _text(self, node):
        if node.nodeType == node.TEXT_NODE:
            return node.nodeValue
        else:
            return "".join(map(self._text, node.childNodes))


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
    def __init__(self, description, correct_answer, expected_results):
        self.description = description
        self.correct_answer = correct_answer
        self.expected_results = expected_results
