from StringIO import StringIO

import sqlexecutor
from sqlexecutor.results import ResultTable
from nose.tools import istest, assert_equal

from learnsomesql.courses import CourseReader


@istest
def creation_sql_is_empty_if_element_not_present():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course></course>"""
    
    course = _read_xml(xml)
    assert_equal([], course.creation_sql)


@istest
def creation_sql_is_read_from_xml():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <creation-sql>create table hats (name);</creation-sql>
        </course>"""
    
    course = _read_xml(xml)
    assert_equal(["create table hats (name);"], course.creation_sql)


@istest
def creation_sql_has_statements_separated_by_blank_lines():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <creation-sql>
                create table hats (name);
            
                create table coats (color);
            </creation-sql>
        </course>"""
    
    course = _read_xml(xml)
    assert_equal(["create table hats (name);", "create table coats (color);"], course.creation_sql)


@istest
def dialect_elements_are_included_if_dialects_match():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <creation-sql>
                <dialect name="sqlite3">create table hats (name);</dialect>
                <dialect name="mysql">create table hats (name varchar(255));</dialect>
            </creation-sql>
        </course>"""
    
    course = _read_xml(xml, dialect="sqlite3")
    assert_equal(["create table hats (name);"], course.creation_sql)


@istest
def lessons_sql_is_empty_if_element_not_present():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course></course>"""
    
    course = _read_xml(xml)
    assert_equal([], course.lessons)


@istest
def lesson_has_slug_and_title_and_description():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <lessons>
                <lesson>
                    <slug>simple-selects</slug>
                    <title>Simple SELECTs</title>
                    <description><p>SELECTs are the simplest SQL statement.</p></description>
                </lesson>
            </lessons>
        </course>"""
    
    course = _read_xml(xml)
    assert_equal(1, len(course.lessons))
    lesson = course.lessons[0]
    assert_equal("simple-selects", lesson.slug)
    assert_equal("Simple SELECTs", lesson.title)
    assert_equal("<p>SELECTs are the simplest SQL statement.</p>", lesson.description)


@istest
def question_has_description_and_correct_query():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <lessons>
                <lesson>
                    <questions>
                        <question>
                            <description>
                                <p>Get all the hats.</p>
                            </description>
                            <correct-query>SELECT * FROM hats</correct-query>
                        </question>
                    </questions>
                </lesson>
            </lessons>
        </course>"""
    
    course = _read_xml(xml)
    
    questions = course.lessons[0].questions
    assert_equal(1, len(questions))
    
    question = questions[0]
    assert_equal("<p>Get all the hats.</p>", question.description)
    assert_equal("SELECT * FROM hats", question.correct_query)


@istest
def question_expected_result_is_result_of_executing_correct_query():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <creation-sql>
                create table hats (name);
            
                insert into hats (name) values ("Fedora");
            </creation-sql>
            <lessons>
                <lesson>
                    <questions>
                        <question>
                            <description>
                                <p>Get all the hats.</p>
                            </description>
                            <correct-query>SELECT * FROM hats</correct-query>
                        </question>
                    </questions>
                </lesson>
            </lessons>
        </course>"""
    
    course = _read_xml(xml)
    
    question = course.lessons[0].questions[0]
    assert_equal(["name"], question.expected_results.column_names)
    assert_equal([["Fedora"]], question.expected_results.rows)


def _read_xml(xml, dialect="sqlite3"):
    sqlexecutor.prepare("sqlite3", None)
    executor = sqlexecutor.executor("sqlite3", None)
    reader = CourseReader(executor)
    return reader.read_file(StringIO(xml), dialect)
