import unittest
from spitfire.compiler.ast import *
from spitfire.compiler import util
from spitfire.compiler import walker
import yappsrt


class BaseTest(unittest.TestCase):

  def _compile(self, template_content):
    template_node = util.parse_template(template_content)
    template_node.source_path = 'test_template.spt'
    return template_node


class TestEscapeHash(BaseTest):

  @staticmethod
  def _def_foo_pred(node):
      return type(node) == DefNode and node.name == 'foo'

  def test_escape_simple(self):
    code = """
#def foo
\#test
#end def
    """
    template = self._compile(code)

    def_node = walker.find_node(template, TestEscapeHash._def_foo_pred)
    text = ''.join([node.value for node in def_node.child_nodes if type(node) == TextNode])
    self.assertEqual(text, '#test')


  def test_backslash_hash_escape(self):
    code = """
#def foo
\\\#test
#end def
    """
    template = self._compile(code)

    def_node = walker.find_node(template, TestEscapeHash._def_foo_pred)
    text = ''.join([node.value for node in def_node.child_nodes if type(node) == TextNode])
    self.assertEqual(text, '\\#test')

  def test_escape_needed(self):
    code = """
#def foo
\#if
#end def
    """
    template = self._compile(code)

    def_node = walker.find_node(template, TestEscapeHash._def_foo_pred)
    text = ''.join([node.value for node in def_node.child_nodes if type(node) == TextNode])
    self.assertEqual(text, '#if')


class TestDo(BaseTest):

  @staticmethod
  def _do_pred(node):
    return type(node) == DoNode

  def test_do_syntax(self):
    code = """
#def foo
#do $bar()
#end def
    """
    template = self._compile(code)
    do_node = walker.find_node(template, TestDo._do_pred)
    if not do_node:
      self.fail('Do node should be present in AST')

  def test_bad_do_syntax(self):
    code = """
#def foo
#do #do $bar()
#end def
    """
    self.assertRaises(yappsrt.FatalParseError, self._compile, code)

  def test_do_expression(self):
    code = """
#def foo
#do 1 + 2
#end def
    """
    template = self._compile(code)

    do_node = walker.find_node(template, TestDo._do_pred)
    if not do_node:
      self.fail('Do node should be present in AST')

class TestAllowRaw(BaseTest):

  @staticmethod
  def _allow_raw_pred(node):
    return type(node) == AllowRawNode

  def test_allow_raw(self):
    code = """
#allow_raw

#def foo
#end def
"""
    template = self._compile(code)

    allow_raw_node = walker.find_node(template, TestAllowRaw._allow_raw_pred)
    if not allow_raw_node:
      self.fail('AllowRawNode should be present in AST')


if __name__ == '__main__':
  unittest.main()
