import argparse
import os
import utils
import jinja2
from proto_schema_parser import Parser, Field, Message
from proto_schema_parser.ast import OneOf, Enum, Package

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as f:
    h_template = jinja2.Template(f.read())
with open("src/templates/wrapper.cpp.j2", "r") as f:
    cpp_template = jinja2.Template(f.read())
with open("src/templates/CMakeLists.txt.j2", "r") as f:
    cmake_template = jinja2.Template(f.read())

if __name__ == "__main__":
    args = parser.parse_args()
    filenames: list[str] = []
    packages_definitions: dict[str, str] = {}

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)

    for proto_filename in os.listdir(args.proto_dir):

        if not proto_filename.endswith(".proto"):
            continue
        filename = proto_filename.split('.proto')[0]

        with open(os.path.join(args.proto_dir, proto_filename), "r") as f:

            schema = Parser().parse(f.read())
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

            print(f'Generating files for {proto_filename}...')

            with open(os.path.join(args.output_dir, f"{filename}.h"), "w") as f:
                f.write(h_template.render(file_elements=schema.file_elements, filename=filename, package=package, utils=utils))
                print(f"✅ Generated header file {os.path.join(args.output_dir, f'{filename}.h')}")
            with open(os.path.join(args.output_dir, "src", f"{filename}.cpp"), "w") as f:
                f.write(cpp_template.render(file_elements=schema.file_elements, filename=filename, package=package, utils=utils))
                print(f"✅ Generated source file {os.path.join(args.output_dir, 'src', f'{filename}.cpp')}", end="\n\n")

    print(f"Generating file for CMake...")

    with open(os.path.join(args.output_dir, "CMakeLists.txt"), "w") as f:
        f.write(cmake_template.render(filenames=filenames))
        print(f"✅ Generated CMake file {os.path.join(args.output_dir, 'CMakeLists.txt')}", end="\n\n")

    print("Generated all files correctly!")
