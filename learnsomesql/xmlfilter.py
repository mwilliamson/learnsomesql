def filter_xml(node, dialect):
    _filter_xml_internal(node, dialect)
    node.normalize()
    return node
    

def _filter_xml_internal(node, dialect):
    for child in node.childNodes:
        _filter_xml_internal(child, dialect)
        
        if child.nodeType == child.ELEMENT_NODE and child.tagName == "dialect":
            if child.getAttribute("name") == dialect:
                for dialect_child in list(child.childNodes):
                    node.insertBefore(dialect_child, child)
            node.removeChild(child)
    


def _concat(elements):
    return "".join(element for element in elements if isinstance(element, basestring))
