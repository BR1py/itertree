import pytest
from itertree import *

__argument__ = 'FAKE'


class ObservableiDataModel(Data.iTDataModel):

    def __init__(self, value=Data.__NOVALUE__, state=True, text='ok'):
        self.state = state
        self.text = text
        super().__init__(value)

    def _validator(self, value):
        return self.state, self.text


@pytest.fixture
def setup_no_argument():
    object_under_test = Data.iTDataModel()
    yield object_under_test


@pytest.fixture
def setup_fake_argument():
    object_under_test = Data.iTDataModel(value=__argument__)
    yield object_under_test


class TestiTDataModelInit:

    def test_init_no_arguments(self, setup_no_argument):
        assert setup_no_argument.value is None and \
               setup_no_argument._formatter_cache is None

    def test_init_value_argument(self, setup_fake_argument):
        assert setup_fake_argument.value == __argument__ and \
               setup_fake_argument._formatter_cache is None

    def test_init_value_invalid_argument(self):
        with pytest.raises(ValueError):
            class_under_test = ObservableiDataModel(value=__argument__, state=False)


class TestiTDataModelProperties:

    def test_is_iTDataModel_property(self, setup_no_argument):
        assert setup_no_argument.is_iTDataModel is True

    def test_is_empty_property(self, setup_no_argument, setup_fake_argument):
        assert setup_no_argument.is_empty is True and setup_fake_argument.is_empty is False

    def test_value_property(self, setup_no_argument, setup_fake_argument):
        assert setup_no_argument.value is None and setup_fake_argument.value is __argument__


class TestiTDataModelMethods:
    state_data = [(True, __argument__),
                  (False, None)]

    def test_clear_value(self, setup_fake_argument):
        assert setup_fake_argument.clear_value() is __argument__ and \
               setup_fake_argument.value is None

    def test_clear_value_empty_value(self, setup_no_argument):
        assert setup_no_argument.clear_value() is None and \
               setup_no_argument.value is None

    def test__validator(self, setup_fake_argument):
        assert setup_fake_argument._validator(None) == (True, 'ok')

    @pytest.mark.parametrize("state, expected", state_data)
    def test_set_state(self, state, expected):
        object_under_test = ObservableiDataModel(state=state)
        if state is False:
            with pytest.raises(TypeError):
                object_under_test.set(expected)
        else:
            object_under_test.set(expected)
            assert object_under_test.value == __argument__
