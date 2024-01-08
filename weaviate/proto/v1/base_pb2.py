# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: v1/base.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\rv1/base.proto\x12\x0bweaviate.v1\x1a\x1cgoogle/protobuf/struct.proto"T\n\x15NumberArrayProperties\x12\x12\n\x06values\x18\x01 \x03(\x01\x42\x02\x18\x01\x12\x11\n\tprop_name\x18\x02 \x01(\t\x12\x14\n\x0cvalues_bytes\x18\x03 \x01(\x0c"7\n\x12IntArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\x03\x12\x11\n\tprop_name\x18\x02 \x01(\t"8\n\x13TextArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\t\x12\x11\n\tprop_name\x18\x02 \x01(\t";\n\x16\x42ooleanArrayProperties\x12\x0e\n\x06values\x18\x01 \x03(\x08\x12\x11\n\tprop_name\x18\x02 \x01(\t"\xd7\x03\n\x15ObjectPropertiesValue\x12\x33\n\x12non_ref_properties\x18\x01 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x43\n\x17number_array_properties\x18\x02 \x03(\x0b\x32".weaviate.v1.NumberArrayProperties\x12=\n\x14int_array_properties\x18\x03 \x03(\x0b\x32\x1f.weaviate.v1.IntArrayProperties\x12?\n\x15text_array_properties\x18\x04 \x03(\x0b\x32 .weaviate.v1.TextArrayProperties\x12\x45\n\x18\x62oolean_array_properties\x18\x05 \x03(\x0b\x32#.weaviate.v1.BooleanArrayProperties\x12\x38\n\x11object_properties\x18\x06 \x03(\x0b\x32\x1d.weaviate.v1.ObjectProperties\x12\x43\n\x17object_array_properties\x18\x07 \x03(\x0b\x32".weaviate.v1.ObjectArrayProperties"^\n\x15ObjectArrayProperties\x12\x32\n\x06values\x18\x01 \x03(\x0b\x32".weaviate.v1.ObjectPropertiesValue\x12\x11\n\tprop_name\x18\x02 \x01(\t"X\n\x10ObjectProperties\x12\x31\n\x05value\x18\x01 \x01(\x0b\x32".weaviate.v1.ObjectPropertiesValue\x12\x11\n\tprop_name\x18\x02 \x01(\t*\x89\x01\n\x10\x43onsistencyLevel\x12!\n\x1d\x43ONSISTENCY_LEVEL_UNSPECIFIED\x10\x00\x12\x19\n\x15\x43ONSISTENCY_LEVEL_ONE\x10\x01\x12\x1c\n\x18\x43ONSISTENCY_LEVEL_QUORUM\x10\x02\x12\x19\n\x15\x43ONSISTENCY_LEVEL_ALL\x10\x03\x42n\n#io.weaviate.client.grpc.protocol.v1B\x11WeaviateProtoBaseZ4github.com/weaviate/weaviate/grpc/generated;protocolb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "v1.base_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"\n#io.weaviate.client.grpc.protocol.v1B\021WeaviateProtoBaseZ4github.com/weaviate/weaviate/grpc/generated;protocol"
    _NUMBERARRAYPROPERTIES.fields_by_name["values"]._options = None
    _NUMBERARRAYPROPERTIES.fields_by_name["values"]._serialized_options = b"\030\001"
    _globals["_CONSISTENCYLEVEL"]._serialized_start = 983
    _globals["_CONSISTENCYLEVEL"]._serialized_end = 1120
    _globals["_NUMBERARRAYPROPERTIES"]._serialized_start = 60
    _globals["_NUMBERARRAYPROPERTIES"]._serialized_end = 144
    _globals["_INTARRAYPROPERTIES"]._serialized_start = 146
    _globals["_INTARRAYPROPERTIES"]._serialized_end = 201
    _globals["_TEXTARRAYPROPERTIES"]._serialized_start = 203
    _globals["_TEXTARRAYPROPERTIES"]._serialized_end = 259
    _globals["_BOOLEANARRAYPROPERTIES"]._serialized_start = 261
    _globals["_BOOLEANARRAYPROPERTIES"]._serialized_end = 320
    _globals["_OBJECTPROPERTIESVALUE"]._serialized_start = 323
    _globals["_OBJECTPROPERTIESVALUE"]._serialized_end = 794
    _globals["_OBJECTARRAYPROPERTIES"]._serialized_start = 796
    _globals["_OBJECTARRAYPROPERTIES"]._serialized_end = 890
    _globals["_OBJECTPROPERTIES"]._serialized_start = 892
    _globals["_OBJECTPROPERTIES"]._serialized_end = 980
# @@protoc_insertion_point(module_scope)
