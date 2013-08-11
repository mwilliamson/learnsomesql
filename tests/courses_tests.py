from StringIO import StringIO

import sqlexecutor
from nose.tools import istest, assert_equal

from learnsomesql.courses import CourseReader


@istest
def creation_sql_is_empty_if_element_no_present():
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


def _read_xml(xml, dialect="sqlite3"):
    sqlexecutor.prepare("sqlite3", None)
    executor = sqlexecutor.executor("sqlite3", None)
    reader = CourseReader(executor)
    return reader.read_file(StringIO(xml), dialect)
