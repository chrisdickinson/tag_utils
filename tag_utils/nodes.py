from surlex import MacroRegistry, Surlex, parsed_surlex_object 
from django import template
import copy

register_macro = MacroRegistry.register

RE_INT = r'\d+|[\w\.]+'
RE_STR = r'\'.*\'|".*"|[\w\.]+'
RE_KWARG = r'([\w\.]+)=(\'.*\'|".*"|[\w\.]+|\d+)'
RE_VAR = r'\w+'


register_macro('int', RE_INT)
register_macro('string', RE_STR)
register_macro('var', RE_VAR)
register_macro('kwarg', RE_KWARG)

def pre_macro_kwarg(value, parser):
    key, value = value.split('=')
    return (key, parser.compile_filter(value))

def post_macro_kwarg(key, value, context):
    return (value[0], value[1].resolve(context))

def post_macro_string(key, value, context):
    value = value.resolve(context)
    if value[0] in ('"', "'"):
        value = value[1:-1]
    return key, value

DEFAULT_MACRO_PREHOOKS = {
    'string':lambda value, parser: parser.compile_filter(value),
    'int':lambda value, parser: parser.compile_filter(value),
    'var':lambda value, parser: value,
    'kwarg':pre_macro_kwarg,
}

DEFAULT_MACRO_POSTHOOKS = {
    'int':lambda key, value, context: (key, int(value.resolve(context))),
    'string':post_macro_string,
    'kwarg':post_macro_kwarg,
}
class ParsedNode(template.Node):
    def __init__(self, function_name, surlex_string, func, macro_pre=None, macro_post=None):
        self.function_name = function_name
        self.surlex = parsed_surlex_object(' '.join([function_name, surlex_string]))
        if macro_pre is None:
            macro_pre = DEFAULT_MACRO_PREHOOKS
        if macro_post is None:
            macro_post = DEFAULT_MACRO_POSTHOOKS 
        self.macro_pre = macro_pre
        self.macro_post = macro_post
        self.func = func

    def __call__(self, parser, token):
        match = self.surlex.match(token.contents)
        if match is None:
            raise template.TemplateSyntaxError('%s failed to match %s against %s.' % (self.function_name, self.surlex, token.contents))
        
        parsed_args = {}
        for key, val in match.iteritems():
            if val is not None and self.surlex.groupmacros[key] in self.macro_pre:
                parsed_args[key] = self.macro_pre[self.surlex.groupmacros[key]](val, parser)
            else:
                parsed_args[key] = val

        cloned_self = copy.deepcopy(self)
        cloned_self.parsed_args = parsed_args
        return cloned_self

    def render(self, context):
        kwargs = {}
        macros = self.surlex.groupmacros
        for key, value in self.parsed_args.iteritems():
            if value is not None:
                if key in self.surlex.groupmacros and self.surlex.groupmacros[key] in self.macro_post:
                    key, value = self.macro_post[self.surlex.groupmacros[key]](key, value, context)
                kwargs.update({
                    str(key):value
                })
        kwargs['context'] = context
        return self.func(**kwargs)

def define_parsed_tag(reg, fn, match):
    obj = ParsedNode(fn.func_name, match, fn)
    return reg.tag(fn.func_name, obj)
