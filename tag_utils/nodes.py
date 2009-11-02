from surlex import MacroRegistry, Surlex, parsed_surlex_object 
from django import template
register_macro = MacroRegistry.register

class ComplexMacro(object):
    def __str__(self):
        return ""

RE_INT = r'\d+|[\w\.]+'
RE_STR = r'\'.*\'|".*"|[\w\.]+'
RE_AS = r'as \w+'
optional = lambda x : ' (%s)' % x

register_macro('int', RE_INT)
register_macro('string', RE_STR)
register_macro('as', RE_AS)
register_macro('optional_int', optional(RE_INT))
register_macro('optional_string', optional(RE_STR))
register_macro('optional_as', optional(RE_AS))

def liberal_getattr(f, key):
    value = None
    if getattr(f, 'has_key', None):
        value = f[key]
    test_attr = getattr(f, key, None)
    if test_attr:
        value = test_attr
    if callable(value):
        value = value()
    if value is None:
        getattr(f, key)
    return value

def statement(context, value):
    value_parts = value.split('.')
    current = context
    value = None
    for part in value_parts:
        current = liberal_getattr(current, part)
    if isinstance(current, str):
        current = "'%s'" % current
    return current

def compose_hook(test_is_literal, post_process):
    def fn(context, value):
        try:
            new_value = value
            if not test_is_literal(value):
                new_value = statement(context, value)
            return post_process(new_value)
        except AttributeError:
            return None
    return fn

def is_string(value):
    if value[0] in ('"', "'"):
        return True

def is_int(value):
    try:
        int(value)
    except ValueError:
        return False
    return True

def to_string(value):
    return str(value[1:-1])

class ParsedNode(template.Node):
    MACRO_HOOKS = {
        'int':compose_hook(is_int, int),
        'optional_int':compose_hook(is_int, int),
        'string':compose_hook(is_string, to_string),
        'optional_string':compose_hook(is_string, to_string),
        'as':compose_hook(lambda x:True, str),
        'optional_as':compose_hook(lambda x:True, str),
    }

    def __init__(self, surlex_string=None):
        if surlex_string:
            self.surlex = parsed_surlex_object(surlex_string)

    def set_parsed_args(self, parsed_args):
        self.parsed_args = parsed_args

    def process_value(self, parser, key, value):
        if key in self.surlex.groupmacros.keys():
            macro = self.surlex.groupmacros[key]
            if macro.startswith('optional'):
                offset = 1
                value = value[offset:]
            if 'as' in macro:
                value = value[3:]
        return value

    def __call__(self, parser, token):
        match = self.surlex.match(token.contents)
        if match is None:
            raise template.TemplateSyntaxError('Failed to match against %s with "%s".' % (self.surlex.regex, token.contents))
        
        parsed_args = dict([(k, self.process_value(parser, k, match[k])) for k in match])
        c_self = self.__class__()
        c_self.surlex = self.surlex
        c_self.set_parsed_args(parsed_args)
        return c_self

    def render(self, context):
        kwargs = {}
        for key in self.surlex.groupmacros.keys():
            macro = self.surlex.groupmacros[key]
            if key in self.parsed_args.keys():
                value = self.parsed_args[key]
                if macro in self.MACRO_HOOKS:
                    value = self.MACRO_HOOKS[macro](context, value)      #transform the value into the right type
                kwargs[str(key)] = value
        try:
            return self.process(context, **kwargs)
        except:
            return ''

    def process(self, context, *args, **kwargs):
        return ""

SINGLE_VALUE = lambda x:x[0]
