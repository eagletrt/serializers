from proto_schema_parser import Parser
from proto_schema_parser.ast import Field, MessageElement, FileElement, Package, MapField, FieldCardinality

TYPES_MAP = {
    "int32": "int32_t",
    "int64": "int64_t",
    "uint32": "uint32_t",
    "uint64": "uint64_t",
    "float": "float",
    "double": "double",
    "bool": "bool",
    "string": "std::string",
    "bytes": "std::string",
    "fixed32": "uint32_t",
    "fixed64": "uint64_t",
    "sfixed32": "int32_t",
    "sfixed64": "int64_t",
    "sint32": "int32_t",
    "sint64": "int64_t"
}

def __typeof(field_type: str) -> str:
    return field_type if field_type not in TYPES_MAP else TYPES_MAP[field_type]

def get_package(file_elements: list[FileElement]) -> Package:
    for file_element in file_elements:
        if isinstance(file_element, Package):
            return file_element
    return None

def set_correct_type(field: MessageElement) -> None:
    if isinstance(field, MapField):
        setattr(field, "type", f"std::map<{__typeof(field.key_type)}, {__typeof(field.value_type)}>")
    elif isinstance(field, Field) and field.cardinality == FieldCardinality.REPEATED:
        field.type = f"std::vector<{__typeof(field.type)}>"
    else:
        field.type = TYPES_MAP[field.type] if field.type in TYPES_MAP else field.type