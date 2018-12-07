'''
Provide serialization and de-serialization of Google's protobuf Messages into/from JSON format.
'''

from google.protobuf.descriptor import FieldDescriptor as FD
from functools import partial
import json


class ParseError(Exception):
    pass


def json2pb(pb, js, useFieldNumber=False):
    ''' 
    Convert JSON string to google.protobuf.descriptor instance 
    '''
    for field in pb.DESCRIPTOR.fields:
        if useFieldNumber:
            key = field.number
        else:
            key = field.name
        if key not in js:
            continue
        if field.type == FD.TYPE_MESSAGE:
            pass
        elif field.type in _js2ftype:
            ftype = _js2ftype[field.type]
        else:
            raise ParseError("Field %s.%s of type '%d' is not supported" % (
                pb.__class__.__name__, field.name, field.type, ))
        value = js[key]
        if field.label == FD.LABEL_REPEATED:
            pb_value = getattr(pb, field.name, None)
            for v in value:
                if field.type == FD.TYPE_MESSAGE:
                    json2pb(pb_value.add(), v, useFieldNumber=useFieldNumber)
                else:
                    pb_value.append(ftype(v))
        else:
            if field.type == FD.TYPE_MESSAGE:
                json2pb(getattr(pb, field.name, None),
                        value, useFieldNumber=useFieldNumber)
            else:
                setattr(pb, field.name, ftype(value))
    return pb


def pb2json(pb, useFieldNumber=False):
    ''' 
    Convert google.protobuf.descriptor instance to JSON string 
    '''
    js = {}
    # fields = pb.DESCRIPTOR.fields #all fields
    fields = pb.ListFields()  # only filled (including extensions)
    for field, value in fields:
        if useFieldNumber:
            key = field.number
        else:
            key = field.name
        if field.type == FD.TYPE_MESSAGE:
            ftype = partial(pb2json, useFieldNumber=useFieldNumber)
        elif field.type in _ftype2js:
            ftype = _ftype2js[field.type]
        else:
            raise ParseError("Field %s.%s of type '%d' is not supported" % (
                pb.__class__.__name__, field.name, field.type, ))
        if field.label == FD.LABEL_REPEATED:
            js_value = []
            for v in value:
                js_value.append(ftype(v))
        else:
            js_value = ftype(value)
        js[key] = js_value
    return js


_ftype2js = {
    FD.TYPE_DOUBLE: float,
    FD.TYPE_FLOAT: float,
    FD.TYPE_INT64: int,
    FD.TYPE_UINT64: int,
    FD.TYPE_INT32: int,
    FD.TYPE_FIXED64: float,
    FD.TYPE_FIXED32: float,
    FD.TYPE_BOOL: bool,
    FD.TYPE_STRING: str,
    # FD.TYPE_MESSAGE: pb2json,              #handled specially
    FD.TYPE_BYTES: lambda x: x.encode('string_escape'),
    FD.TYPE_UINT32: int,
    FD.TYPE_ENUM: int,
    FD.TYPE_SFIXED32: float,
    FD.TYPE_SFIXED64: float,
    FD.TYPE_SINT32: int,
    FD.TYPE_SINT64: int,
}

_js2ftype = {
    FD.TYPE_DOUBLE: float,
    FD.TYPE_FLOAT: float,
    FD.TYPE_INT64: int,
    FD.TYPE_UINT64: int,
    FD.TYPE_INT32: int,
    FD.TYPE_FIXED64: float,
    FD.TYPE_FIXED32: float,
    FD.TYPE_BOOL: bool,
    FD.TYPE_STRING: str,
    # FD.TYPE_MESSAGE: json2pb,     #handled specially
    FD.TYPE_BYTES: lambda x: x.decode('string_escape'),
    FD.TYPE_UINT32: int,
    FD.TYPE_ENUM: int,
    FD.TYPE_SFIXED32: float,
    FD.TYPE_SFIXED64: float,
    FD.TYPE_SINT32: int,
    FD.TYPE_SINT64: int,
}
