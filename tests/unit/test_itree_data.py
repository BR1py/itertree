"""
This code is taken from the itertree package:
  _ _____ _____ _____ _____ _____ _____ _____
 | |_   _|   __| __  |_   _| __  |   __|   __|
 |-| | | |   __|    -| | | |    -|   __|   __|
 |_| |_| |_____|__|__| |_| |__|__|_____|_____|

https://pypi.org/project/itertree/
GIT Home:
https://github.com/BR1py/itertree
The documentation can be found here:
https://itertree.readthedocs.io/en/latest/index.html

The code is published under MIT license
For more information see: https://en.wikipedia.org/wiki/MIT_License

CONTENT DESCRIPTION:

Unit tests related to the itertree data types
"""

import pytest
import sys
from itertree import *

__argument__ = 'FAKE'


class ObservableiDataModel(Data.iTDataModel):

    def __init__(self, value=Data.__NOVALUE__, state=True):
        self.state = state
        super().__init__(value)


    def validator(self, value):
        if not self.state:
            raise Data.iTDataTypeError
        return value

    def formatter(self, value=None):
        if value is None or value is NoValue:
            if self.is_empty:
                return 'None'
            value = self._value
        return str(value)

    def get_init_args(self):
        return (self._value,self.state)

class FakeModel:
    def __init__(self):
        pass
    def clear(self):
        pass

@pytest.fixture
def setup_no_argument():
    object_under_test = ObservableiDataModel()
    yield object_under_test


@pytest.fixture
def setup_fake_argument():
    object_under_test = ObservableiDataModel(value=__argument__)
    yield object_under_test


class TestiTDataModelInit:

    def test_init_no_arguments(self, setup_no_argument):
        assert setup_no_argument.value is NoValue
        assert setup_no_argument._formatter_cache is None

    def test_init_value_argument(self, setup_fake_argument):
        assert setup_fake_argument.value == __argument__
        assert setup_fake_argument._formatter_cache is None

    def test_init_value_invalid_argument(self):
        with pytest.raises(Data.iTDataTypeError):
            class_under_test = ObservableiDataModel(value=__argument__, state=False)


class TestiTDataModelProperties:

    def test_is_empty_property(self, setup_no_argument, setup_fake_argument):
        assert setup_no_argument.is_empty is True
        assert setup_fake_argument.is_empty is False

    def test_value_property(self, setup_no_argument, setup_fake_argument):
        assert setup_no_argument.value is NoValue
        assert setup_fake_argument.value == __argument__


class TestiTDataModelMethods:
    state_data = [(True, __argument__),
                  (False, None)]

    def test_clear_value(self, setup_fake_argument):
        assert setup_fake_argument.clear() == __argument__
        assert setup_fake_argument.value is NoValue

    def test_clear_value_empty_value(self, setup_no_argument):
        assert setup_no_argument.clear() is NoValue
        assert setup_no_argument.value is NoValue

    def test_emptyformatter_empty(self, setup_no_argument):
        assert setup_no_argument.formatter() == 'None'

    def test_emptyformatter_not_empty(self, setup_fake_argument):
        assert setup_fake_argument.formatter() == 'FAKE'

    def test_formatter_empty(self, setup_no_argument):
        assert setup_no_argument.formatter('Kraftfahrzeug-Haftpflichtversicherung') == \
               'Kraftfahrzeug-Haftpflichtversicherung'

    def test_formatter_empty_not_empty(self, setup_fake_argument):
        assert setup_fake_argument.formatter('Massenkommunikationsdienstleistungsunternehmen') == \
               'Massenkommunikationsdienstleistungsunternehmen'

    @pytest.mark.parametrize("state, expected", state_data)
    def test_set_state(self, state, expected):
        object_under_test = ObservableiDataModel(state=state)
        if state is False:
            with pytest.raises(Data.iTDataTypeError):
                object_under_test.set(expected)
        else:
            object_under_test.set(expected)
            assert object_under_test.value == __argument__

    def test_contains(self, setup_fake_argument):
       assert __argument__ in setup_fake_argument

    def test_not_contains(self, setup_fake_argument):
       assert None not in setup_fake_argument

    def test_contains_empty(self, setup_no_argument):
       assert Data.__NOVALUE__ in setup_no_argument

    def test_contains_none(self):
        object_under_test = ObservableiDataModel(value=None)
        assert None in object_under_test

    def test_not_contains_empty(self, setup_no_argument):
       assert __argument__ not in setup_no_argument

    def test_format_empty_no_format_spec(self, setup_no_argument):
        assert format(setup_no_argument) == 'None'

    def test_no_format_spec(self, setup_fake_argument):
        assert format(setup_fake_argument) == __argument__

    def test_inequality(self, setup_no_argument, setup_fake_argument):
        assert setup_no_argument != setup_fake_argument

    def test_equality(self, setup_fake_argument):
        object_under_test = ObservableiDataModel(value=__argument__)
        assert object_under_test == setup_fake_argument

    def test_inequality_2(self, setup_fake_argument):
        object_under_test = ObservableiDataModel(value=__argument__)
        assert not (object_under_test != setup_fake_argument)

    def test_equality_2(self, setup_fake_argument):
        object_under_test = ObservableiDataModel()
        assert not(object_under_test == setup_fake_argument)

    @pytest.mark.xfail(reason='Issue in formatter')
    def test_format_spec(self):
        # Failing here.
        assert format(ObservableiDataModel(10), 'x') == 'a'

    def test_repr_empty(self, setup_no_argument):
        assert str(setup_no_argument) == 'ObservableiDataModel()'

    def test_repr_not_empty(self, setup_fake_argument):
        assert str(setup_fake_argument) == 'ObservableiDataModel(value= %s)' %__argument__

__raw_data__ = 'raw_data'
@pytest.fixture
def iTData_setup():
    fake_model = ObservableiDataModel()
    object_under_test = Data.iTData({__raw_data__: fake_model})
    yield object_under_test

@pytest.fixture
def iTData_setup_no_argument():
    object_under_test = Data.iTData()
    yield object_under_test

@pytest.fixture
def iTData_setup_no_key_model():
    object_under_test = Data.iTData()
    fake_model = ObservableiDataModel()
    fake_model.value = 10
    object_under_test.__setitem__(fake_model)
    yield object_under_test

@pytest.fixture
def iTData_setup_key_with_model():
    object_under_test = Data.iTData()
    fake_model = ObservableiDataModel()
    fake_model.value = 10
    object_under_test.__setitem__(key='ten',value=fake_model)
    yield object_under_test

@pytest.fixture
def iTData_setup_nokey():
    object_under_test = Data.iTData()
    object_under_test.__setitem__('one')
    yield object_under_test

@pytest.fixture
def iTData_as_dict():
    object_under_test = Data.iTData({'one': 1, 'two': 2, 'three': 3})
    yield object_under_test

@pytest.fixture
def iterable_fixture():
    return [('one', 1),('two', 2), ('three', 3)]

@pytest.fixture
def dictionary_fixture():
    return {'one': 1,'two': 2, 'three': 3}

@pytest.fixture
def model_dictionary_fixture():
    fake_model = ObservableiDataModel()
    fake_model.value = 1
    fake_model_2 = ObservableiDataModel()
    fake_model_2.value = 2
    fake_model_3 = ObservableiDataModel()
    fake_model_3.value = 3
    return {'one': fake_model,'two': fake_model_2, 'three': fake_model_3}

@pytest.fixture
def model_iterable_fixture():
    fake_model = ObservableiDataModel()
    fake_model.value = 1
    fake_model_2 = ObservableiDataModel()
    fake_model_2.value = 2
    fake_model_3 = ObservableiDataModel()
    fake_model_3.value = 3
    return [('one', fake_model),('two', fake_model_2), ('three', fake_model_3)]



class TestiTDataInit:

    def test_init_no_arguments(self, iTData_setup_no_argument):
        assert not bool(iTData_setup_no_argument)

    def test_init_value_argument(self, iTData_setup):
        assert __raw_data__ in iTData_setup and bool(iTData_setup)

    def test_init_type_error(self):
        object_under_test = Data.iTData((1,2,3))
        assert bool(object_under_test)
        assert Data.__NOKEY__ in object_under_test.keys()
        assert object_under_test[Data.__NOKEY__] == (1,2,3)

    def test_init_value_error(self):
        object_under_test = Data.iTData({'Hello'})
        assert bool(object_under_test)
        assert Data.__NOKEY__ in object_under_test.keys()
        assert object_under_test[Data.__NOKEY__] == {'Hello'}

    def test_init_no_seq_one_keyword(self):
        object_under_test = Data.iTData(one=1)
        assert object_under_test['one'] == 1

    def test_init_no_key_and_keyword(self):
        object_under_test = Data.iTData((1, 2, 3), nine=9)
        assert not object_under_test.is_no_key_only


class TestiTDataProperties:

    def test_is_empty(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        assert object_under_test.is_empty

    def test_is_not_empty(self, iTData_setup):
        object_under_test = iTData_setup
        assert not object_under_test.is_empty

    def test_is_no_key_only(self):
        object_under_test = Data.iTData((1,2,3))
        assert object_under_test.is_no_key_only

    def test_is_no_key_only_2(self):
        object_under_test = Data.iTData((1, 2, 3), nine=9)
        assert not object_under_test.is_no_key_only


class TestiTDataSetItemMethod:

    def test_idata__setitem__normal_set(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        object_under_test['one'] = 1
        assert object_under_test['one'] == 1

    def test_idata__setitem___no_value(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        al = object_under_test.__setitem__('one')
        assert 'one' in object_under_test.values()

    def test_idata__setitem___no_value_with_model(self, iTData_setup_no_argument):
        fake_model = ObservableiDataModel()
        object_under_test = iTData_setup_no_argument
        object_under_test.__setitem__(fake_model)
        assert fake_model in object_under_test.values()

    def test__setitem___model(self, iTData_setup):
        object_under_test = iTData_setup
        object_under_test.__setitem__(key=__raw_data__, value=10)
        assert object_under_test[__raw_data__] == 10

    def test_setitem_key_exception(self, iTData_setup_no_argument):
        if int(sys.version.split('.')[1])<12:
            # This exception comes only in python versions < 3.12
            with pytest.raises(TypeError):
                object_under_test = iTData_setup_no_argument
                object_under_test.__setitem__(key=slice(6), value=10)


class TestiTDataGetItemMethod:
    key_values = [(Data.STR,'10'), (Data.VALUE,10)]
    none_values =[(Data.STR,'None'), (Data.VALUE, None)]

    @pytest.mark.parametrize("return_type, value", key_values)
    def test___get_item_key_value_model(self, iTData_setup, return_type, value):
        object_under_test = iTData_setup
        object_under_test[__raw_data__] = 10
        assert object_under_test.__getitem__(__raw_data__, _return_type=return_type) == value

    def test___get_item__key_value__model_2(self, iTData_setup):
        object_under_test = iTData_setup
        object_under_test[__raw_data__] = 10
        assert object_under_test.__getitem__(__raw_data__, _return_type=Data.FULL) == 10

    @pytest.mark.parametrize("return_type, value", none_values)
    def test___get_item__key_value_model_none(self, iTData_setup, return_type, value):
        object_under_test = iTData_setup
        assert object_under_test.__getitem__(__raw_data__, _return_type=return_type) in {'None',NoValue}

    def test___get_item__key_value_model_none_2(self, iTData_setup):
        object_under_test = iTData_setup
        assert object_under_test.__getitem__(__raw_data__, _return_type=Data.FULL).value is NoValue

    @pytest.mark.parametrize("return_type, value", key_values)
    def test___get_item_no_key_mode_value(self, iTData_setup_no_argument, return_type, value):
        object_under_test = iTData_setup_no_argument
        fake_model = ObservableiDataModel()
        fake_model.value = 10
        object_under_test.__setitem__(fake_model)
        assert object_under_test.__getitem__(Data.__NOKEY__ , _return_type=return_type) == value

    def test___get_item_no_key_model_value_2(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        fake_model = ObservableiDataModel()
        fake_model.value = 10
        object_under_test.__setitem__(fake_model)
        assert object_under_test.__getitem__(Data.__NOKEY__ , _return_type=Data.FULL).value == 10

    @pytest.mark.parametrize("return_type, value", none_values)
    def test___get_item_no_key_none_model_value(self, iTData_setup_no_argument, return_type, value):
        object_under_test = iTData_setup_no_argument
        fake_model = ObservableiDataModel()
        object_under_test.__setitem__(fake_model)
        assert object_under_test.__getitem__(Data.__NOKEY__, _return_type=return_type) in {value,NoValue}

    def test___get_item_no_key_none_model_value_2(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        fake_model = ObservableiDataModel()
        object_under_test.__setitem__(fake_model)
        assert object_under_test.__getitem__(Data.__NOKEY__, _return_type=Data.FULL).value is NoValue


class TestiTDataDelItemMethod:

    def test_del_item_model(self, iTData_setup):
        with pytest.raises(KeyError):
            object_under_test = iTData_setup
            object_under_test.__delitem__(__raw_data__, _value_only=False)
            object_under_test[__raw_data__]

    def test_del_item_model_no_key(self, iTData_setup_no_key_model):
        with pytest.raises(KeyError):
            object_under_test = iTData_setup_no_key_model
            object_under_test.__delitem__(_value_only=False)
            object_under_test[Data.__NOKEY__]

    def test_del_item_model_value_only_true(self, iTData_setup):
        object_under_test = iTData_setup
        object_under_test.__delitem__(__raw_data__)
        with pytest.raises(KeyError):
            assert object_under_test.__getitem__(__raw_data__) is None

    #def test_del_item_model_no_key_value_only_true(self, iTData_setup_no_key_model):
    #    object_under_test = iTData_setup_no_key_model
    #    object_under_test.__delitem__()
    #    # Is this correct? If alue is NoValue the return value changes from the
    #    # value to the container. No it should deliver directly None Adapted the test-case
    #    assert object_under_test[Data.__NOKEY__] is None

    def test_del_item_exception(self, iTData_setup):
        with pytest.raises(KeyError):
            object_under_test = iTData_setup
            object_under_test.__delitem__('NON-EXISTING-KEY')

    def test_del_attribute_error(self, iTData_as_dict):
        object_under_test = iTData_as_dict
        object_under_test.__delitem__('one')
        assert 'one' not in object_under_test.keys()

    def test_del_type_error(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        fake_model = FakeModel()
        object_under_test['TEST'] = fake_model
        object_under_test.__delitem__('TEST')
        assert 'TEST' not in object_under_test.keys()


class TestHash:
    def test_hash(self, iTData_as_dict):
        object_under_test = iTData_as_dict
        # As long as there is not exception here, everything alright.
        hash(object_under_test)


class TestRepr:

    def test_empty_repr(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        assert repr(object_under_test) == '%s()' % (object_under_test.__class__.__name__)

    def test_no_key_only(self, iTData_setup_nokey):
        object_under_test = iTData_setup_nokey
        assert repr(object_under_test) == '%s(%s)' % (object_under_test.__class__.__name__, repr(object_under_test.__getitem__(Data.__NOKEY__)))

    def test_normal(self, iTData_as_dict):
        object_under_test = iTData_as_dict
        representation = repr(object_under_test)
        for key, item in object_under_test.items():
            string_repr = "\'"+str(key) + "\'"+': ' + str(item)
            assert string_repr in representation
        assert object_under_test.__class__.__name__ in representation


class TestUpdate:

    def test_update_with_nothing(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        object_under_test.update()
        assert len(object_under_test) == 0

    def test_update_with_keyword(self, iTData_setup_no_argument):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(nine=9, ten=10)
        assert 'nine' in object_under_test
        assert 'ten' in object_under_test
        assert len(object_under_test) == 2

    def test_update_with_dictionary(self, iTData_setup_no_argument, dictionary_fixture):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(dictionary_fixture)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert len(object_under_test) == 3

    def test_update_with_dictionary_and_keyword(self, iTData_setup_no_argument, dictionary_fixture):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(dictionary_fixture, ten=70)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert object_under_test['ten'] == 70
        assert len(object_under_test) == 4

    def test_update_with_iterable(self, iTData_setup_no_argument, iterable_fixture):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(iterable_fixture)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert len(object_under_test) == 3

    def test_update_with_iterable_and_keyword(self, iTData_setup_no_argument, iterable_fixture):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(iterable_fixture, ten=70)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert object_under_test['ten'] == 70
        assert len(object_under_test) == 4

    def test_mode_update_with_nothing(self, iTData_setup_no_key_model):
        object_under_test = iTData_setup_no_key_model
        object_under_test.update()
        assert len(object_under_test) == 1

    def test_mode_update_with_keyword(self, iTData_setup_key_with_model):
        object_under_test = iTData_setup_key_with_model
        object_under_test.update(ten=70, nine=9)
        assert object_under_test['ten'] == 70
        assert object_under_test['nine'] == 9
        assert len(object_under_test) == 2

    def test_model_update_with_dictionary(self, iTData_setup_no_argument, model_dictionary_fixture):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(model_dictionary_fixture)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert len(object_under_test) == 3

    def test_model_update_with_dictionary_and_keyword(self, iTData_setup_key_with_model, model_dictionary_fixture):
        object_under_test = iTData_setup_key_with_model
        object_under_test.update(model_dictionary_fixture, ten=70)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert object_under_test['ten'] == 70
        assert len(object_under_test) == 4

    def test_model_update_with_iterable(self, iTData_setup_no_argument, model_iterable_fixture):
        object_under_test = iTData_setup_no_argument
        object_under_test.update(model_iterable_fixture)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert len(object_under_test) == 3

    def test_model_update_with_iterable_and_keyword(self, iTData_setup_key_with_model, model_iterable_fixture):
        object_under_test = iTData_setup_key_with_model
        object_under_test.update(model_iterable_fixture, ten=70)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3
        assert object_under_test['ten'] == 70
        assert len(object_under_test) == 4


class TestiTDataDictionaryConsistency:

    def test_init_key_with_kwargs(self):
        object_under_test = Data.iTData(one = 1, two = 2, three = 3)
        assert bool(object_under_test)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3

    def test_init_with_mapping(self):
        object_under_test = Data.iTData({'one': 1, 'two': 2, 'three': 3})
        assert bool(object_under_test)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3

    def test_init_with_iterable(self):
        object_under_test = Data.iTData(zip(['one', 'two', 'three'], [1, 2, 3]))
        assert bool(object_under_test)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3

    def test_init_with_iterable_2(self):
        object_under_test = Data.iTData([('two', 2), ('one', 1), ('three', 3)])
        assert bool(object_under_test)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3

    def test_init_with_generator(self):
        def dict_generator():
                var = (('one', 1),('two', 2),('three', 3))
                for elem in var:
                    yield elem

        object_under_test = Data.iTData(dict_generator())
        assert bool(object_under_test)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3

    def test_init_with_dict_comprehension(self):
        object_under_test = Data.iTData({x: x ** 2 for x in (1, 2, 3)})
        assert bool(object_under_test)
        assert object_under_test[1] == 1
        assert object_under_test[2] == 4
        assert object_under_test[3] == 9

    def test_init_with_mapping_and_keyword(self):
        object_under_test = Data.iTData({'one': 1, 'three': 3}, two=2)
        assert bool(object_under_test)
        assert object_under_test['one'] == 1
        assert object_under_test['two'] == 2
        assert object_under_test['three'] == 3

    def test_method_clear(self, iTData_as_dict):
        empty_dict = iTData_as_dict.clear()
        assert not bool(iTData_as_dict)

    def test_method___contains__(self, iTData_as_dict):
        assert 'two' in iTData_as_dict

    def test_method_copy(self, iTData_as_dict):
        copied_dict = iTData_as_dict.copy()
        assert copied_dict == iTData_as_dict

    def test_method___del_item__(self, iTData_as_dict):
        del iTData_as_dict['two']
        assert 'two' not in iTData_as_dict

    def test_method_fromkeys(self):
        object_under_test = Data.iTData.fromkeys(['one', 'two', 'three'])
        values = set(object_under_test.values())
        assert (len(object_under_test) == 3)
        assert (values == {None})

    def test_method_fromkeys_with_values(self):
        object_under_test = Data.iTData.fromkeys(['one', 'two', 'three'], (5))
        values = set(object_under_test.values())
        assert (len(object_under_test) == 3)
        assert (values == {5})

    def test_method_get(self, iTData_as_dict):
        assert iTData_as_dict.get('two', 3) == 2
        assert iTData_as_dict.get('ten', 3) == 3

    def test_method___get_item__exception(self, iTData_as_dict):
        with pytest.raises(KeyError):
            iTData_as_dict.__getitem__('ten')

    def test_method___get_item__(self, iTData_as_dict):
        assert iTData_as_dict.__getitem__('two') == 2

    def test_method_items(self, iTData_as_dict):
        view = iTData_as_dict.items()
        assert Data.iTData(view) == iTData_as_dict

    def test_method___iter__(self, iTData_as_dict):
        iterator = iter(iTData_as_dict)
        assert list(iterator) == list(iTData_as_dict.keys())

    def test_method_keys(self, iTData_as_dict):
        assert set(iTData_as_dict.keys()) == {'one', 'two', 'three'}

    def test_method_len(self, iTData_as_dict):
        assert len(iTData_as_dict) == 3

    def test_method_pop(self, iTData_as_dict):
        popped_value = iTData_as_dict.pop('one')
        assert popped_value == 1
        assert len(iTData_as_dict) == 2
        assert 'one' not in iTData_as_dict

    def test_method_pop_missing(self, iTData_as_dict):
        popped_value = iTData_as_dict.pop('ten', 'MISSING VALUE')
        assert popped_value == 'MISSING VALUE'
        assert len(iTData_as_dict) == 3

    def test_method_pop_missing_2(self, iTData_as_dict):
        with pytest.raises(KeyError):
            popped_value = iTData_as_dict.pop('ten')

    def test_method_pop_item(self, iTData_as_dict):
        iTData_as_dict.popitem()
        assert len(iTData_as_dict) == 2

    def test_method_setdefault(self, iTData_as_dict):
        iTData_as_dict.setdefault('ten', []).append(10)
        assert iTData_as_dict['ten'] == [10]

    def test_method_setdefault(self, iTData_as_dict):
        iTData_as_dict.setdefault('two', []).__repr__()
        assert iTData_as_dict.setdefault('two', []).__repr__() == '2'

    def test_method___setitem__(self, iTData_as_dict):
        iTData_as_dict.__setitem__('ten', 10)
        assert iTData_as_dict['ten'] == 10

    def test_method___setitem__existing(self, iTData_as_dict):
        iTData_as_dict.__setitem__('two', 10)
        assert iTData_as_dict['two'] == 10

    def test_method_update_with_iterable(self, iTData_as_dict):
        iTData_as_dict.update(zip(['four', 'five', 'six'], [4, 5, 6]))
        assert len(iTData_as_dict) == 6
        assert iTData_as_dict['four'] == 4
        assert iTData_as_dict['five'] == 5
        assert iTData_as_dict['six'] == 6

    def test_method_update_with_mapping(self, iTData_as_dict):
        iTData_as_dict.update({'four':4, 'five':5, 'six':6})
        assert len(iTData_as_dict) == 6
        assert iTData_as_dict['four'] == 4
        assert iTData_as_dict['five'] == 5
        assert iTData_as_dict['six'] == 6

    def test_method_update_with_kwargs(self, iTData_as_dict):
        iTData_as_dict.update(four=4, five=5, six=6)
        assert len(iTData_as_dict) == 6
        assert iTData_as_dict['four'] == 4
        assert iTData_as_dict['five'] == 5
        assert iTData_as_dict['six'] == 6

    def test_method_update_with_iterable_and_kwargs(self, iTData_as_dict):
        iTData_as_dict.update(zip(['seven', 'eight', 'nine'], [7, 8, 9]), four=4, five=5, six=6)

        assert len(iTData_as_dict) == 9
        assert iTData_as_dict['four'] == 4
        assert iTData_as_dict['five'] == 5
        assert iTData_as_dict['six'] == 6
        assert iTData_as_dict['seven'] == 7
        assert iTData_as_dict['eight'] == 8
        assert iTData_as_dict['nine'] == 9

    def test_method_update_with_mapping_and_kwargs(self, iTData_as_dict):
        iTData_as_dict.update()
        iTData_as_dict.update({'seven':7, 'eight':8, 'nine':9}, four=4, five=5, six=6)

        assert len(iTData_as_dict) == 9
        assert iTData_as_dict['four'] == 4
        assert iTData_as_dict['five'] == 5
        assert iTData_as_dict['six'] == 6
        assert iTData_as_dict['seven'] == 7
        assert iTData_as_dict['eight'] == 8
        assert iTData_as_dict['nine'] == 9

    def test_method_values(self, iTData_as_dict):
        assert set(iTData_as_dict.values()) == {1, 2, 3}
