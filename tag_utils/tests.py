from django.test import TestCase
from nodes import ParsedNode, ParsedBlock, define_parsed_tag, define_parsed_block
from django.template import TemplateSyntaxError

class token_mock(object):
    def __init__(self, string):
        self.contents = string

class filter_mock(object):
    def __init__(self, val):
        self.val = val

    def resolve(self, context):
        return self.val

class parser_mock(object):
    def compile_filter(self, value):
        return filter_mock(value)

class ParsedNodeTests(TestCase):
    def test_call_clones(self):
        def test(context):
            pass
        p = ParsedNode('test', '<anything:string>', lambda context, anything: '')
        new_p = p(parser_mock(), token_mock("test 'things'"))
        self.assertFalse(p is new_p)
        self.assertEqual(p.function_name, new_p.function_name)

    def test_no_match(self):
        def test(context):
            pass
        p = ParsedNode('test', '<anything:string> <required:int>', lambda context, anything, required: '')
        self.assertRaises(TemplateSyntaxError, p.__call__, parser_mock(), token_mock("test 'fail'"))

    def test_hooks_are_called(self):
        hooks_called = {
            'pre':0,
            'post':0,
        }

        def prehook(value, parser):
            hooks_called['pre'] = 1
            return parser.compile_filter(value)

        def posthook(key, value, context):
            hooks_called['post'] = 1
            return key, value.resolve(context)

        hooks = (
            {'int':prehook},
            {'int':posthook},
        )

        p = ParsedNode('test', '<thing:int>', lambda context, thing: thing, *hooks)
        new_p = p(parser_mock(), token_mock('test 2'))
        rendered = new_p.render({})
        self.assertEqual(hooks_called['pre'], 1)
        self.assertEqual(hooks_called['post'], 1)

    def test_values_are_unpacked(self):
        expected_unpacked = {
            'arg1':0,
            'arg2':0,
            'usrkey':0,
        }
        token = token_mock('test 1 "thing" usrkey=2')

        def test_expected(context, *args, **kwargs):
            for key in kwargs:
                if key in expected_unpacked:
                    expected_unpacked[key] = kwargs[key] 
            return '' 

        p = ParsedNode('test', '<arg1:int> <arg2:string> <kw:kwarg>', test_expected) 
        new_p = p(parser_mock(), token)
        result = new_p.render({})
        self.assertEqual(expected_unpacked['arg1'], 1)
        self.assertEqual(expected_unpacked['arg2'], 'thing')
        self.assertEqual(expected_unpacked['usrkey'], '2')

    def test_actually_parsing_works(self):
        from django.template import builtins
        from django.template import Library
        from django.template import Template
        def test_parse(context, thing1, thing2, asvar=None):        
            return u' '.join([str(thing1), thing2, str(asvar)])

        templates = [
            "{% test_parse 1 obj.val as var %}",
            "{% test_parse obj.fn 'string' %}",
        ]

        class test_object(object):
            val = 'string'
            def fn(self):
                return 1

        register = Library()
        register.tag('test_parse', ParsedNode('test_parse', '<thing1:int> <thing2:string>( as <asvar:var>)', test_parse))
        builtins.append(register)

        context = {
            'obj':test_object()
        }

        templates_cmp = [Template(template) for template in templates]
        results = [t.render(context) for t in templates_cmp]
        self.assertEqual(results[0], '1 string var')
        self.assertEqual(results[1], '1 string None')

    def test_fail_on_parse(self):
        from django.template import builtins
        from django.template import Library
        from django.template import Template
        def test_not_enough_args(context):        
            return 'this should never ever run'

        templates = [
            "{% test_parse 1 obj.val as var %}",
            "{% test_parse obj.fn 'string' %}",
        ]

        class test_object(object):
            val = 'string'
            def fn(self):
                return 1

        register = Library()
        register.tag('test_parse', ParsedNode('test_parse', '<thing1:int> <thing2:string>( as <asvar:var>)', test_not_enough_args))
        builtins.append(register)

        context = {
            'obj':test_object()
        }

        templates_cmp = [Template(template) for template in templates]
        for i in templates_cmp:
            self.assertRaises(TemplateSyntaxError, i.render, context) 


class ParsedBlockTests(TestCase):
    pass

class HelperTests(TestCase):
    pass 

