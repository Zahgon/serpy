from serpy.fields import Field
import operator
import six


class SerializerBase(Field):
    _field_map = {}


def _compile_field_to_tuple(field, name, serializer_cls):
    pass


class SerializerMeta(type):

    @staticmethod
    def _get_fields(direct_fields, serializer_cls):
        pass

    @staticmethod
    def _compile_fields(field_map, serializer_cls):
        pass

    def __new__(cls, name, bases, attrs):
        # Fields declared directly on the class.
        direct_fields = {}

        # Take all the Fields from the attributes.
        for attr_name, field in attrs.items():
            if isinstance(field, Field):
                direct_fields[attr_name] = field
        for k in direct_fields.keys():
            del attrs[k]

        real_cls = super(SerializerMeta, cls).__new__(cls, name, bases, attrs)

        field_map = cls._get_fields(direct_fields, real_cls)
        compiled_fields = cls._compile_fields(field_map, real_cls)

        real_cls._field_map = field_map
        real_cls._compiled_fields = tuple(compiled_fields)
        return real_cls


class Serializer(six.with_metaclass(SerializerMeta, SerializerBase)):
    """:class:`Serializer` is used as a base for custom serializers.

    The :class:`Serializer` class is also a subclass of :class:`Field`, and can
    be used as a :class:`Field` to create nested schemas. A serializer is
    defined by subclassing :class:`Serializer` and adding each :class:`Field`
    as a class variable:

    Example: ::

        class FooSerializer(Serializer):
            foo = Field()
            bar = Field()

        foo = Foo(foo='hello', bar=5)
        FooSerializer(foo).data
        # {'foo': 'hello', 'bar': 5}

    :param instance: The object or objects to serialize.
    :param bool many: If ``instance`` is a collection of objects, set ``many``
        to ``True`` to serialize to a list.
    :param context: Currently unused parameter for compatability with Django
        REST Framework serializers.
    """
    #: The default getter used if :meth:`Field.as_getter` returns None.
    default_getter = operator.attrgetter

    def __init__(self, instance=None, many=False, data=None, context=None,
                 **kwargs):
        if data is not None:
            raise RuntimeError(
                'serpy serializers do not support input validation')

        super(Serializer, self).__init__(**kwargs)
        self.instance = instance
        self.many = many
        self._data = None

    def _serialize(self, instance, fields):
        pass

    def to_value(self, instance):
        pass

    @property
    def data(self):
        """Get the serialized data from the :class:`Serializer`.

        The data will be cached for future accesses.
        """
        pass


class DictSerializer(Serializer):
    """:class:`DictSerializer` serializes python ``dicts`` instead of objects.

    Instead of the serializer's fields fetching data using
    ``operator.attrgetter``, :class:`DictSerializer` uses
    ``operator.itemgetter``.

    Example: ::

        class FooSerializer(DictSerializer):
            foo = IntField()
            bar = FloatField()

        foo = {'foo': '5', 'bar': '2.2'}
        FooSerializer(foo).data
        # {'foo': 5, 'bar': 2.2}
    """
    default_getter = operator.itemgetter
