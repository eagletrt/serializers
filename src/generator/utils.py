from proto_schema_parser import Parser
from proto_schema_parser.ast import Message, FileElement, Package, Enum, File
import os

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

def typeof(field_type: str, elements_names: list) -> str:
    if field_type in elements_names:
        return field_type
    elif field_type in TYPES_MAP:
        return TYPES_MAP[field_type]
    else:
        print(f"Field type '{field_type}' is not valid, aborting...")
        exit(1)

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

def load_files(directory_path: str) -> (list[(str, (Package, File))], dict[str, str]):

    # (filename, (package, file_schema))
    files: list[(str, (Package, File))] = []
    definitions: dict[str, str] = {}

    for filename in os.listdir(directory_path):

        # Skip non-proto files
        if not filename.endswith(".proto"):
            continue

        # Read and parse schema
        with open(os.path.join(directory_path, filename), "r") as f:
            schema = Parser().parse(f.read())
        filename = filename.split('.proto')[0]

        # Throw error if package has not set
        package = get_package(schema.file_elements)
        if package is None:
            print(f"No package found for file {filename}.proto, aborting")
            exit(1)
        schema.file_elements.remove(package)

        # Check multiple package definition
        if get_package(schema.file_elements) is not None:
            print(f"Multiple package definition for file {filename}.proto, aborting...")
            exit(1)

        # Append schema and definitions to the lists
        files.append((filename, (package, schema)))
        if not package.name in definitions:
            definitions[package.name] = []

        # Check multiple definitions
        for element in schema.file_elements:
            if element is None:
                schema.file_elements.remove(element)
                continue
            if element.name in definitions[package.name]:
                print(f"Multiple definition of element {package.name}.{element.name}, aborting...")
                exit(1)
            definitions[package.name].append(element.name)

    return (files, definitions)
