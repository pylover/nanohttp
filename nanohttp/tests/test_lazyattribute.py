from nanohttp import LazyAttribute


def test_lazyattribute():
    global callcount
    class MyType:
        pass
    my_instance = MyType()

    callcount = 0
    class O:
        @LazyAttribute
        def attr1(self):
            """Attribute 1"""
            global callcount
            callcount += 1
            return my_instance

    assert 'Attribute 1' == O.attr1.__doc__
    assert 'attr1' == O.attr1.__name__

    o = O()
    assert my_instance is o.attr1
    assert my_instance is o.attr1
    assert my_instance is o.attr1
    assert 1 == callcount

