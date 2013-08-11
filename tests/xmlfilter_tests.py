from xml.dom import minidom, Node

import sqlexecutor
from nose.tools import istest, assert_equal

from learnsomesql.xmlfilter import filter_xml


@istest
def xml_without_dialects_is_unchanged():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <creation-sql>create table hats (name);</creation-sql>
        </course>"""
    
    filtered_xml = _filter_xml_string(xml, dialect="sqlite3")
    creation_sql_element = filtered_xml.getElementsByTagName("creation-sql")[0]
    assert_equal(1, len(creation_sql_element.childNodes))
    assert_equal(Node.TEXT_NODE, creation_sql_element.childNodes[0].nodeType)
    assert_equal("create table hats (name);", creation_sql_element.childNodes[0].nodeValue)


@istest
def text_content_of_dialect_node_is_included_if_dialect_matches():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <course>
            <creation-sql>
                <dialect name="sqlite3">create table hats (name);</dialect>
                <dialect name="mysql">create table hats (name varchar(255));</dialect>
            </creation-sql>
        </course>"""
    
    
    filtered_xml = _filter_xml_string(xml, dialect="sqlite3")
    creation_sql_element = filtered_xml.getElementsByTagName("creation-sql")[0]
    assert_equal(1, len(creation_sql_element.childNodes))
    assert_equal(Node.TEXT_NODE, creation_sql_element.childNodes[0].nodeType)
    assert_equal("create table hats (name);", creation_sql_element.childNodes[0].nodeValue.strip())


@istest
def children_of_dialect_node_are_included_if_dialect_matches():
    xml = """<?xml version="1.0" encoding="utf-8" ?>
        <description>
            It's <dialect name="sqlite3">really <strong>great</strong>!</dialect><dialect name="mysql">about <strong>so-so</strong>.</dialect>
        </description>"""
    
    
    filtered_xml = _filter_xml_string(xml, dialect="sqlite3")
    creation_sql_element = filtered_xml.getElementsByTagName("description")[0]
    assert_equal(3, len(creation_sql_element.childNodes))
    
    assert_equal(Node.TEXT_NODE, creation_sql_element.childNodes[0].nodeType)
    assert_equal("\n            It's really ", creation_sql_element.childNodes[0].nodeValue)
    
    assert_equal(Node.ELEMENT_NODE, creation_sql_element.childNodes[1].nodeType)
    assert_equal("strong", creation_sql_element.childNodes[1].tagName)
    
    assert_equal(Node.TEXT_NODE, creation_sql_element.childNodes[2].nodeType)
    assert_equal("!\n        ", creation_sql_element.childNodes[2].nodeValue)


def _filter_xml_string(xml, dialect):
    return filter_xml(minidom.parseString(xml), dialect)

