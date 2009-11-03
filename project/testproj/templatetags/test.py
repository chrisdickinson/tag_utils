from tag_utils import define_parsed_tag, define_parsed_block 
from django import template
register = template.Library()

def test_parsed(context, arg1, arg2, asvar=None):
    if asvar is None:
        asvar = '<None>'
    return u"%d %s as %s" % (arg1, arg2, asvar)

def test_kwargs(context, yarg):
    return u"%s" % yarg

def test_block(context, nodelist, **kwargs):
    output = ['starting test_block<br />']
    context.push()
    context.update(kwargs)
    output.append(nodelist.render(context))
    context.pop()
    output.append('exiting test_block')
    return '\n'.join(output)

define_parsed_tag(register, test_parsed, r'<arg1:int> <arg2:string>( as <asvar:var>)')
define_parsed_tag(register, test_kwargs, r'<kw:kwarg>')
define_parsed_block(register, test_block, r'<kw:kwarg>')
