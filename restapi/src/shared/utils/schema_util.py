import inspect
import json

from schematics import Model
from schematics.types.base import (BaseType, NumberType, IntType, LongType, FloatType,
                                   DecimalType, BooleanType)
from schematics.types.compound import ModelType, ListType

__version__ = '1.0'


SCHEMATIC_TYPE_TO_JSON_TYPE = {
    NumberType: 'number',
    IntType: 'integer',
    LongType: 'integer',
    FloatType: 'number',
    DecimalType: 'number',
    BooleanType: 'boolean',
    ListType : 'array',
    ModelType : 'object',
}

# Schema Serialization

# Parameters for serialization to JSONSchema
schema_kwargs_to_schematics = {
    'maxLength': 'max_length',
    'minLength': 'min_length',
    'pattern': 'regex',
    'minimum': 'min_value',
    'maximum': 'max_value',
}

def model_to_json_schema(model):
    return create_schema(model)

def create_schema(something):
    if inspect.isclass(something) and issubclass(something, Model):
        return create_model_schema(something)
    if isinstance(something, ModelType):
        return create_model_schema(something.model_class)
    if isinstance(something, ListType):
        return create_array_schema(something.field)
    if isinstance(something, BaseType):
        return create_basic_schema(something.__class__)


def create_model_schema(model):
    properties = {}
    required = []
    for field_name, field_instance in model._fields.items():
        serialized_name = getattr(field_instance, 'serialized_name', None) or field_name
        properties[serialized_name] = create_schema(field_instance)

    if getattr(field_instance, 'required', False):
        required.append(serialized_name)
    return {
        'properties':properties,
        'type':'object',
        'title':model.__name__,
        'required':required,
    }

def create_array_schema(innerType):
    return {
        'type':'array',
        'items':create_schema(innerType)
    }
    pass

def create_basic_schema(type):
    return {
        "type": SCHEMATIC_TYPE_TO_JSON_TYPE.get(type, 'string')
    }