from tag_utils import ParsedNode
from django import template
register = template.Library()
class TestParsedNode(ParsedNode):
    def process(self, context, arg1, arg2, asvar=None):
        if asvar is None:
            asvar = '<None>'
        return u"%d %s as %s" % (arg1, arg2, asvar)

register.tag('test_also_parsed', TestParsedNode(r'test_parsed <arg1:int> <arg2:string>(<asvar:optional_string>)'))
register.tag('test_parsed', TestParsedNode(r'test_parsed <arg1:int> <arg2:string>(<asvar:optional_as>)'))
