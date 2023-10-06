import argparse
import os
import json
import proto_utils
import jinja2
from proto_schema_parser import Parser, Field, Message
from proto_schema_parser.ast import OneOf

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of .proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as f:
    cpp_template = jinja2.Template(f.read())

if __name__ == "__main__":
    args = parser.parse_args()

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    os.path.isdir(args.output_dir) or parser.error(f"{args.output_dir} is not a directory")

    for filename in os.listdir(args.proto_dir):

        print(filename)

        if not filename.endswith(".proto"):
            continue

        with open(os.path.join(args.proto_dir, filename), "r") as f:
            schema = Parser().parse(f.read())
            package = proto_utils.get_package(schema.file_elements)
            messages = list(filter(lambda e: isinstance(e, Message), schema.file_elements))
            print(schema)

            if package is None:
                print("No package found for file {filename}, aborting")
                exit(1)

            for message in list(filter(lambda e: isinstance(e, Message),schema.file_elements)):
                for field in message.elements:
                    proto_utils.set_correct_type(field)

            with open(os.path.join(args.output_dir, "inc", f"{package.name}.h"), "w") as f:
                f.write(cpp_template.render(messages=messages, package=package))

