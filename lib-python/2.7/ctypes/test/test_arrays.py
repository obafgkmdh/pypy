import unittest
from ctypes import *
from test.test_support import impl_detail

from ctypes.test import need_symbol

formats = "bBhHiIlLqQfd"

# c_longdouble commented out for PyPy, look at the commend in test_longdouble
formats = c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint, \
          c_long, c_ulonglong, c_float, c_double #, c_longdouble

class ArrayTestCase(unittest.TestCase):

    @impl_detail('long double not supported by PyPy', pypy=False)
    def test_longdouble(self):
        """
        This test is empty. It's just here to remind that we commented out
        c_longdouble in "formats". If pypy will ever supports c_longdouble, we
        should kill this test and uncomment c_longdouble inside formats.
        """

    def test_simple(self):
        # create classes holding simple numeric types, and check
        # various properties.

        init = range(15, 25)

        for fmt in formats:
            alen = len(init)
            int_array = ARRAY(fmt, alen)

            ia = int_array(*init)
            # length of instance ok?
            self.assertEqual(len(ia), alen)

            # slot values ok?
            values = [ia[i] for i in range(len(init))]
            self.assertEqual(values, init)

            # change the items
            from operator import setitem
            new_values = range(42, 42+alen)
            [setitem(ia, n, new_values[n]) for n in range(alen)]
            values = [ia[i] for i in range(len(init))]
            self.assertEqual(values, new_values)

            # are the items initialized to 0?
            ia = int_array()
            values = [ia[i] for i in range(len(init))]
            self.assertEqual(values, [0] * len(init))

            # Too many initializers should be caught
            self.assertRaises(IndexError, int_array, *range(alen*2))

        CharArray = ARRAY(c_char, 3)

        ca = CharArray("a", "b", "c")

        # Should this work? It doesn't:
        # CharArray("abc")
        self.assertRaises(TypeError, CharArray, "abc")

        self.assertEqual(ca[0], "a")
        self.assertEqual(ca[1], "b")
        self.assertEqual(ca[2], "c")
        self.assertEqual(ca[-3], "a")
        self.assertEqual(ca[-2], "b")
        self.assertEqual(ca[-1], "c")

        self.assertEqual(len(ca), 3)

        # slicing is now supported, but not extended slicing (3-argument)!
        from operator import getslice, delitem
        self.assertRaises(TypeError, getslice, ca, 0, 1, -1)

        # cannot delete items
        self.assertRaises(TypeError, delitem, ca, 0)

    def test_numeric_arrays(self):

        alen = 5

        numarray = ARRAY(c_int, alen)

        na = numarray()
        values = [na[i] for i in range(alen)]
        self.assertEqual(values, [0] * alen)

        na = numarray(*[c_int()] * alen)
        values = [na[i] for i in range(alen)]
        self.assertEqual(values, [0]*alen)

        na = numarray(1, 2, 3, 4, 5)
        values = [i for i in na]
        self.assertEqual(values, [1, 2, 3, 4, 5])

        na = numarray(*map(c_int, (1, 2, 3, 4, 5)))
        values = [i for i in na]
        self.assertEqual(values, [1, 2, 3, 4, 5])

    def test_classcache(self):
        self.assertIsNot(ARRAY(c_int, 3), ARRAY(c_int, 4))
        self.assertIs(ARRAY(c_int, 3), ARRAY(c_int, 3))

    def test_from_address(self):
        # Failed with 0.9.8, reported by JUrner
        p = create_string_buffer("foo")
        sz = (c_char * 3).from_address(addressof(p))
        self.assertEqual(sz[:], "foo")
        self.assertEqual(sz[::], "foo")
        self.assertEqual(sz[::-1], "oof")
        self.assertEqual(sz[::3], "f")
        self.assertEqual(sz[1:4:2], "o")
        self.assertEqual(sz.value, "foo")

    @need_symbol('create_unicode_buffer')
    def test_from_addressW(self):
        p = create_unicode_buffer("foo")
        sz = (c_wchar * 3).from_address(addressof(p))
        self.assertEqual(sz[:], "foo")
        self.assertEqual(sz[::], "foo")
        self.assertEqual(sz[::-1], "oof")
        self.assertEqual(sz[::3], "f")
        self.assertEqual(sz[1:4:2], "o")
        self.assertEqual(sz.value, "foo")

    def test_cache(self):
        # Array types are cached internally in the _ctypes extension,
        # in a WeakValueDictionary.  Make sure the array type is
        # removed from the cache when the itemtype goes away.  This
        # test will not fail, but will show a leak in the testsuite.

        # Create a new type:
        class my_int(c_int):
            pass
        # Create a new array type based on it:
        t1 = my_int * 1
        t2 = my_int * 1
        self.assertIs(t1, t2)

if __name__ == '__main__':
    unittest.main()
