import argparse
import os
import re

import jinja2
import utils

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as file:
    h_template = jinja2.Template(file.read())

with open("src/templates/wrapper.cpp.j2", "r") as file:
    cpp_template = jinja2.Template(file.read())

with open("src/templates/serializers.h.j2", "r") as file:
    serializers_template = jinja2.Template(file.read())

with open("src/templates/__init__.py.j2", "r") as file:
    init_template = jinja2.Template(file.read())

with open("src/templates/CMakeLists.txt.j2", "r") as file:
    cmake_template = jinja2.Template(file.read())

with open("src/templates/wrapper.py.j2", "r") as file:
    py_template = jinja2.Template(file.read())

with open("src/templates/test.py.j2", "r") as file:
    test_py_template = jinja2.Template(file.read())

with open("src/templates/conftest.py.j2", "r") as file:
    conftest_template = jinja2.Template(file.read())

if __name__ == "__main__":
    os.system("pre-commit install")

    args = parser.parse_args()

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    (files, package_definitions) = utils.load_files(args.proto_dir)
    os.makedirs(os.path.join(args.output_dir, "proto"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "inc"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)
    
    filenames = []
    filepaths = []

    test_dir = "tests"

    for (filename, filepath, package, schema) in files:
        filenames.append(filename)
        filepaths.append(filepath)

        print(f"Generating python files for {filename}.proto...")
        os.makedirs(os.path.join(args.output_dir, "py", filepath), exist_ok=True)
        with open(os.path.join(args.output_dir, "py", filepath, f"{filename}.py"), "w") as file:
            file.write(py_template.render(file_elements=schema.file_elements, filename=filename, package=package, package_definitions=package_definitions, utils=utils))
            print(f"✅ Generated python file {os.path.join(args.output_dir, 'py', f'{filename}.py')}", end="\n\n")

        print(f"Generating python tests for {filename}.proto...")
        os.makedirs(os.path.join(test_dir, filepath), exist_ok=True)
        with open(os.path.join(test_dir, filepath, f"test_{filename}.py"), "w") as file:
            file.write(test_py_template.render(file_elements=schema.file_elements, output_dir=args.output_dir, filename=filename, package=package, package_definitions=package_definitions, utils=utils))
            print(f"✅ Generated python test file {os.path.join('tests', f'test_{filename}.py')}", end="\n\n")
        with open(os.path.join(test_dir, filepath, f"__init__.py"), "w") as file:
            pass
        
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
    with open(os.path.join(args.output_dir, "py", "__init__.py"), "w") as file:
        file.write(init_template.render(output_dir= args.output_dir, filenames=filenames, filepaths=filepaths))
        print(f"✅ Generated python file {os.path.join(args.output_dir, '__init__.py')}", end="\n\n")

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

    # Generate conftest.py
    with open("tests/conftest.py", "w") as file:
        file.write(conftest_template.render(output_dir= args.output_dir))
    with open("tests/__init__.py", "w") as file:
        pass

    # write .proto_sources.txt with all .proto in output_dir
    if os.path.exists(os.path.join("scripts", ".proto_sources.txt")):
        os.remove(os.path.join("scripts", ".proto_sources.txt"))
    with open(os.path.join("scripts", ".proto_sources.txt"), "w") as file:
        for i, filepath in enumerate(filepaths):
            file.write(f"{os.path.join(args.output_dir, 'proto', filepath, f'{filenames[i]}.proto')}\n")
        print(f"✅ Generated {os.path.join(args.output_dir, '.proto_sources.txt')}", end="\n\n")
