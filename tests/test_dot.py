# test_dot.py
# flake8: noqa

import itertools

import pytest

from graphviz.dot import Graph, Digraph


@pytest.fixture(params=[Graph, Digraph]) 
def cls(request):
    return request.param


@pytest.fixture(params=list(itertools.permutations([Graph, Digraph], 2))) 
def classes(request):
    return request.param


def test_copy(cls):
    c = cls()
    assert c.__class__ is cls
    assert c.copy() is not c
    assert c.copy() is not c.copy()
    assert c.copy().__class__ is c.__class__
    assert c.copy().__dict__ == c.__dict__


def test__repr_svg_(mocker, cls):
    c = cls()
    kwargs = {'return_value.decode.return_value': mocker.sentinel.decoded}
    pipe = mocker.patch.object(c, 'pipe', **kwargs)

    assert c._repr_svg_() is mocker.sentinel.decoded

    pipe.assert_called_once_with(format='svg')
    pipe.return_value.decode.assert_called_once_with(c.encoding)


def test_iter_subgraph_strict(cls):
    with pytest.raises(ValueError) as e:
        cls().subgraph(cls(strict=True))
    e.match(r'strict')


def test_iter_strict():
    assert Graph(strict=True).source == 'strict graph {\n}'
    assert Digraph(strict=True).source == 'strict digraph {\n}'


def test_attr_invalid_kw(cls):
    with pytest.raises(ValueError) as e:
        cls().attr('spam')
    e.match(r'attr')


def test_attr_kw_none():
    dot = Graph()
    dot.attr(spam='eggs')
    assert dot.source == 'graph {\n\tspam=eggs\n}'


def test_subgraph_graph_none():
    dot = Graph()
    with dot.subgraph(name='name', comment='comment'):
        pass
    assert dot.source == 'graph {\n\t// comment\n\tsubgraph name {\n\t}\n}'


def test_subgraph_graph_notsole(cls):
    with pytest.raises(ValueError) as e:
        cls().subgraph(cls(), name='spam')
    e.match(r'sole')


def test_subgraph_mixed(classes):
    cls1, cls2 = classes
    with pytest.raises(ValueError) as e:
        cls1().subgraph(cls2())
    e.match(r'kind')


def test_subgraph_reflexive():  # guard against potential infinite loop
    dot = Graph()
    dot.subgraph(dot)
    assert dot.source == 'graph {\n\t{\n\t}\n}'


def test_subgraph():
    s1 = Graph()
    s1.node('A')
    s1.node('B')
    s1.node('C')
    s1.edge('A', 'B', constraint='false')
    s1.edges(['AC', 'BC'])

    s2 = Graph()
    s2.node('D')
    s2.node('E')
    s2.node('F')
    s2.edge('D', 'E', constraint='false')
    s2.edges(['DF', 'EF'])

    dot = Graph()
    dot.subgraph(s1)
    dot.subgraph(s2)
    dot.attr('edge', style='dashed')
    dot.edges(['AD', 'BE', 'CF'])

    assert dot.source == '''graph {
	{
		A
		B
		C
			A -- B [constraint=false]
			A -- C
			B -- C
	}
	{
		D
		E
		F
			D -- E [constraint=false]
			D -- F
			E -- F
	}
	edge [style=dashed]
		A -- D
		B -- E
		C -- F
}'''


def test_label_html():
    """http://www.graphviz.org/doc/info/shapes.html#html"""
    dot = Digraph('structs', node_attr={'shape': 'plaintext'})
    dot.node('struct1', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR>
    <TD>left</TD>
    <TD PORT="f1">middle</TD>
    <TD PORT="f2">right</TD>
  </TR>
</TABLE>>''')
    dot.node('struct2', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR>
    <TD PORT="f0">one</TD>
    <TD>two</TD>
  </TR>
</TABLE>>''')
    dot.node('struct3', '''<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
  <TR>
    <TD ROWSPAN="3">hello<BR/>world</TD>
    <TD COLSPAN="3">b</TD>
    <TD ROWSPAN="3">g</TD>
    <TD ROWSPAN="3">h</TD>
  </TR>
  <TR>
    <TD>c</TD>
    <TD PORT="here">d</TD>
    <TD>e</TD>
  </TR>
  <TR>
    <TD COLSPAN="3">f</TD>
  </TR>
</TABLE>>''')
    dot.edge('struct1:f1', 'struct2:f0')
    dot.edge('struct1:f2', 'struct3:here')
    assert dot.source == '''digraph structs {
	node [shape=plaintext]
	struct1 [label=<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR>
    <TD>left</TD>
    <TD PORT="f1">middle</TD>
    <TD PORT="f2">right</TD>
  </TR>
</TABLE>>]
	struct2 [label=<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
  <TR>
    <TD PORT="f0">one</TD>
    <TD>two</TD>
  </TR>
</TABLE>>]
	struct3 [label=<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
  <TR>
    <TD ROWSPAN="3">hello<BR/>world</TD>
    <TD COLSPAN="3">b</TD>
    <TD ROWSPAN="3">g</TD>
    <TD ROWSPAN="3">h</TD>
  </TR>
  <TR>
    <TD>c</TD>
    <TD PORT="here">d</TD>
    <TD>e</TD>
  </TR>
  <TR>
    <TD COLSPAN="3">f</TD>
  </TR>
</TABLE>>]
		struct1:f1 -> struct2:f0
		struct1:f2 -> struct3:here
}'''
