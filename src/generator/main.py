import argparse
import os
import re
import utils
import jinja2

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

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    (files, package_definitions) = utils.load_files(args.proto_dir)
    os.makedirs(os.path.join(args.output_dir, "proto"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "inc"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)
    
    filenames = []
    filepaths = []

    for (filename, filepath, package, schema) in files:
        filenames.append(filename)
        filepaths.append(filepath)
        
        print(f'Generating files for {filename}.proto...')
        os.makedirs(os.path.join(args.output_dir, "inc", filepath), exist_ok=True)
        with open(os.path.join(args.output_dir, "inc", filepath, f"{filename}.h"), "w") as file:
            file.write(h_template.render(file_elements=schema.file_elements, filename=filename, package=package, package_definitions=package_definitions, utils=utils))
            print(f"✅ Generated header file {os.path.join(args.output_dir, f'{filename}.h')}")
        os.makedirs(os.path.join(args.output_dir, "src", filepath), exist_ok=True)
        with open(os.path.join(args.output_dir, "src", filepath, f"{filename}.cpp"), "w") as file:
            file.write(cpp_template.render(file_elements=schema.file_elements, filename=filename, filepath=filepath, package=package, utils=utils))
            print(f"✅ Generated source file {os.path.join(args.output_dir, 'src', f'{filename}.cpp')}", end="\n\n")


    print(f"Generating header file...")
    with open(os.path.join(args.output_dir, "serializers.h"), "w") as file:
        file.write(serializers_template.render(filenames=filenames, filepaths=filepaths))
        print(f"✅ Generated header file {os.path.join(args.output_dir, 'serializers.h')}", end="\n\n")

    print(f"Generating file for CMake...")
    with open(os.path.join(args.output_dir, "CMakeLists.txt"), "w") as file:
        file.write(cmake_template.render(filenames=filenames, filepaths=filepaths))
        print(f"✅ Generated CMake file {os.path.join(args.output_dir, 'CMakeLists.txt')}", end="\n\n")

    print(f"Copying .proto files in '{args.proto_dir}/proto/' directory...")    
    for i, filepath in enumerate(filepaths):
        with open(os.path.join(args.proto_dir, filepath, f'{filenames[i]}.proto'), "r") as source:
            os.makedirs(os.path.join(args.output_dir, "proto", filepath), exist_ok=True)
            with open(os.path.join(args.output_dir, 'proto', filepath, f'{filenames[i]}.proto'), "w") as destination:
                result = re.sub(r'package\s+', r'package Pb', source.read())
                destination.write(result)

    print("✅ Copied .proto files")
