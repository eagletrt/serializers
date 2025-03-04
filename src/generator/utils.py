import os

from proto_schema_parser import Parser
from proto_schema_parser.ast import Enum, File, FileElement, Message, Package

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

TYPES_MAP_PY = {
    "int32": "int",
    "int64": "int",
    "uint32": "int",
    "uint64": "int",
    "float": "float",
    "double": "float",
    "bool": "bool",
    "string": "str",
    "bytes": "bytes",
    "fixed32": "int",
    "fixed64": "int",
    "sfixed32": "int",
    "sfixed64": "int",
    "sint32": "int",
    "sint64": "int",
    "string": "str",
}


def typeof(field_type: str, elements_names: list) -> str:
    if field_type in elements_names:
        return field_type
    elif field_type in TYPES_MAP:
        return TYPES_MAP[field_type]
    else:
        print(f"Field type '{field_type}' is not valid, aborting...")
        exit(1)

def typeof_py(field_type: str, elements_names: list) -> str:
    if field_type in elements_names:
        return field_type
    elif field_type in TYPES_MAP:
        return TYPES_MAP_PY[field_type]
    else:
        print(f"Field type '{field_type}' is not valid, aborting...")
        exit(1)

def to_lower_case(string: str) -> str:
    return string.lower()

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

def dir_file_paths(dir, ext):
    files_paths = []
        
    for entry in os.scandir(dir):        
        if entry.is_dir():
            files_paths.extend(dir_file_paths(entry, ext))
        elif entry.is_file():
            if os.path.splitext(entry.name)[1].lower() == ext:
                files_paths.append(entry.path)
        
    return files_paths

def load_files(directory_path: str) -> (list[(str, (Package, File))], dict[str, str]):

    # (filename, (package, file_schema))
    files: list[(str, (Package, File))] = []
    package_definitions: dict[str, str] = {}
    
    for filepath in dir_file_paths(directory_path, '.proto'):

        # Read and parse schema
        with open(filepath, "r") as file:
            schema = Parser().parse(file.read())
            
        filepath = filepath.split('proto/')[1]
        filename = filepath.split('/')[-1]
        filepath = filepath.split(filename)[0]
        filename = filename.split('.proto')[0]
        
        # Throw error if package has not set
        package = get_package(schema.file_elements)
        if package is None:
            print(f'No package found for file {filename}.proto, aborting')
            exit(1)
        schema.file_elements.remove(package)

        # Check multiple package definition
        if get_package(schema.file_elements) is not None:
            print(f'Multiple package definition for file {filename}.proto, aborting...')
            exit(1)

        # Append schema and definitions to the lists
        files.append((filename, filepath, package, schema))
        
        if not package.name in package_definitions:
            package_definitions[package.name] = []

        # Check multiple definitions
        for element in schema.file_elements:
            if element is None:
                schema.file_elements.remove(element)
                continue
            if element.name in package_definitions[package.name]:
                print(f'Multiple definition of element {package.name}.{element.name}, aborting...')
                exit(1)
            package_definitions[package.name].append(element.name)

    return (files, package_definitions)
