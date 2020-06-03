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


def jsonschema_for_fields(model):
    properties = {}
    required = []
    # Loop over each field and either evict it or convert it
    for field_name, field_instance in model._fields.items():
        # Break 3-tuple out
        print (field_name, field_instance)
        serialized_name = getattr(field_instance, 'serialized_name', None) or field_name
        print ("--",isinstance(field_instance, ModelType),isinstance(field_instance, ListType))

        properties[serialized_name] = {
            "type": SCHEMATIC_TYPE_TO_JSON_TYPE.get(field_instance.__class__, 'string')
        }
        if isinstance(field_instance, ModelType):
            properties[serialized_name][field_instance.model_class.__name__] = jsonschema_for_model(field_instance.model_class)

        elif isinstance(field_instance, ListType):
            properties[serialized_name] = jsonschema_for_model(field_instance.field.__class__, 'array')

        # Convert field as single model
        elif isinstance(field_instance, BaseType):
            properties[serialized_name] = {
                "type": SCHEMATIC_TYPE_TO_JSON_TYPE.get(field_instance.__class__, 'string')
            }

        if getattr(field_instance, 'required', False):
            required.append(serialized_name)

    return properties, required


def jsonschema_for_model(model, _type='object'):
    print (model)
    properties, required = jsonschema_for_fields(model)

    schema = {
        'type': _type,
        'title': model.__name__,
        'properties': properties,
    }

    if required:
        schema['required'] = required

    # if _type == 'array':
    #     schema = {
    #         'type': 'array',
    #         'title': '%s Set' % (model.__name__),
    #         'items': schema,
    #     }

    return schema


def to_jsonschema(model):
    """Returns a representation of this schema class as a JSON schema."""
    return json.dumps(jsonschema_for_model(model))