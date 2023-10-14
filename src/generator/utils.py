from proto_schema_parser import Parser
from proto_schema_parser.ast import Field, Message, FileElement, Package, MapField, FieldCardinality, Enum

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

def typeof(field_type: str) -> str:
    return field_type if field_type not in TYPES_MAP else TYPES_MAP[field_type]

def get_package(file_elements: list[FileElement]) -> Package:
    for file_element in file_elements:
        if isinstance(file_element, Package):
            return file_element
    return None

def is_enum(field_type: str, file_elements: list) -> bool:
    filtered = list(filter(lambda e: isinstance(e, Enum), file_elements))
    return field_type in list(map(lambda f: f.name, filtered))

def is_message(field_type: str, file_elements: list) -> bool:
    filtered = list(filter(lambda e: isinstance(e, Message), file_elements))
    return field_type in list(map(lambda f: f.name, filtered))