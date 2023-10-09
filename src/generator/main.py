import argparse
import os
import json
import proto_utils
import jinja2
from proto_schema_parser import Parser, Field, Message
from proto_schema_parser.ast import OneOf, Enum

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of .proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as f:
    h_template = jinja2.Template(f.read())
# with open("src/templates/wrapper.cc.j2", "r") as f:
#     cpp_template = jinja2.Template(f.read())

if __name__ == "__main__":
    args = parser.parse_args()

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    os.makedirs(os.path.join(args.output_dir, "inc"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)

    for filename in os.listdir(args.proto_dir):

        print(filename)

        if not filename.endswith(".proto"):
            continue

        with open(os.path.join(args.proto_dir, filename), "r") as f:

            schema = Parser().parse(f.read())

            package = proto_utils.get_package(schema.file_elements)
            messages = list(filter(lambda e: isinstance(e, Message), schema.file_elements))
            enums = list(filter(lambda e: isinstance(e, Enum), schema.file_elements))

            if package is None:
                print("No package found for file {filename}, aborting")
                exit(1)

            for file_element in list(filter(lambda e: isinstance(e, Message),schema.file_elements)):
                for field in file_element.elements:
                    proto_utils.set_correct_type(field)

            with open(os.path.join(args.output_dir, "inc", f"{package.name}.h"), "w") as f:
                f.write(h_template.render(messages=messages, enums=enums, package=package))
            # with open(os.path.join(args.output_dir, "src", f"{package.name}.cpp"), "w") as f:
            #     f.write(cpp_template.render(messages=messages, package=package))
