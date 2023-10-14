import argparse
import os
import json
import utils
import jinja2
from proto_schema_parser import Parser, Field, Message
from proto_schema_parser.ast import OneOf, Enum, Package

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of .proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as f:
    h_template = jinja2.Template(f.read())
with open("src/templates/wrapper.cpp.j2", "r") as f:
    cc_template = jinja2.Template(f.read())
with open("src/templates/CMakeLists.txt.j2", "r") as f:
    cmake_template = jinja2.Template(f.read())

if __name__ == "__main__":
    args = parser.parse_args()
    packages: list[Package] = []

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)

    for filename in os.listdir(args.proto_dir):

        if not filename.endswith(".proto"):
            continue

        with open(os.path.join(args.proto_dir, filename), "r") as f:

            schema = Parser().parse(f.read())

            package = utils.get_package(schema.file_elements)
            messages = list(filter(lambda e: isinstance(e, Message), schema.file_elements))
            enums = list(filter(lambda e: isinstance(e, Enum), schema.file_elements))

            if package is None:
                print(f"No package found for file {filename}, aborting")
                exit(1)
            else:
                if package.name in list(map(lambda p: p.name, packages)):
                    print(f"Error: multiple proto package '{package.name}' definition. Aborting...")
                    exit(1)
                packages.append(package)
                schema.file_elements.remove(package)


            with open(os.path.join(args.output_dir, f"{package.name}.h"), "w") as f:
                f.write(h_template.render(file_elements=schema.file_elements, package=package, utils=utils))
            with open(os.path.join(args.output_dir, "src", f"{package.name}.cpp"), "w") as f:
                f.write(cc_template.render(file_elements=schema.file_elements, package=package, utils=utils))

    with open(os.path.join(args.output_dir, "CMakeLists.txt"), "w") as f:
        f.write(cmake_template.render(packages=packages))

