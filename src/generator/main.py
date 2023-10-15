import argparse
import os
import utils
import jinja2
from proto_schema_parser import Parser, Field, Message
from proto_schema_parser.ast import OneOf, Enum, Package

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as file:
    h_template = jinja2.Template(file.read())
    
with open("src/templates/wrapper.cpp.j2", "r") as file:
    cpp_template = jinja2.Template(file.read())
    
with open("src/templates/serializers.h.j2", "r") as file:
    serializers_template = jinja2.Template(file.read())
    
with open("src/templates/CMakeLists.txt.j2", "r") as file:
    cmake_template = jinja2.Template(file.read())

if __name__ == "__main__":
    args = parser.parse_args()
    filenames: list[str] = []
    packages_definitions: dict[str, str] = {}

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    os.makedirs(os.path.join(args.output_dir, "proto"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "inc"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)

    for proto_filename in os.listdir(args.proto_dir):

        if not proto_filename.endswith(".proto"):
            continue
        filename = proto_filename.split('.proto')[0]

        with open(os.path.join(args.proto_dir, proto_filename), "r") as proto_file:
            proto_file_content = proto_file.read()

            schema = Parser().parse(proto_file_content)
            package = utils.get_package(schema.file_elements)

            if package is None:
                print(f"No package found for file {proto_filename}, aborting")
                exit(1)

            if not package.name in packages_definitions:
                packages_definitions[package.name] = []
            filenames.append(filename)

            for element in schema.file_elements:
                if element.__class__.__name__ != "Package" and element.name in packages_definitions[package.name]:
                    print(f"Multiple definition of element {package.name}.{element.name}, aborting...")
                    exit(1)
                packages_definitions[package.name].append(element.name)

            print(f'Generating files for {proto_filename}...\n')
            
            with open(os.path.join(args.output_dir, "proto", f"{filename}.proto"), "w") as file:
                file.write(proto_file_content)
                print(f"✅ Generated proto  file {os.path.join(args.output_dir, f'{filename}.proto')}")

            with open(os.path.join(args.output_dir, "inc", f"{filename}.h"), "w") as file:
                file.write(h_template.render(file_elements=schema.file_elements, filename=filename, package=package, utils=utils))
                print(f"✅ Generated header file {os.path.join(args.output_dir, f'{filename}.h')}")
                
            with open(os.path.join(args.output_dir, "src", f"{filename}.cpp"), "w") as file:
                file.write(cpp_template.render(file_elements=schema.file_elements, filename=filename, package=package, utils=utils))
                print(f"✅ Generated source file {os.path.join(args.output_dir, 'src', f'{filename}.cpp')}", end="\n\n")

    print(f"Generating header file...")
    with open(os.path.join(args.output_dir, "serializers.h"), "w") as file:
        file.write(serializers_template.render(filenames=filenames))
        print(f"✅ Generated header file {os.path.join(args.output_dir, 'serializers.h')}", end="\n\n")

    print(f"Generating file for CMake...")
    with open(os.path.join(args.output_dir, "CMakeLists.txt"), "w") as file:
        file.write(cmake_template.render(filenames=filenames))
        print(f"✅ Generated CMake  file {os.path.join(args.output_dir, 'CMakeLists.txt')}", end="\n")
