import argparse
import os
import utils
import jinja2

parser = argparse.ArgumentParser(description='Generate cpp code from proto schemas')

parser.add_argument("proto_dir", type=str, help="directory path of proto files")
parser.add_argument("output_dir", type=str, help="directory path of generated files")

with open("src/templates/wrapper.h.j2", "r") as f:
    h_template = jinja2.Template(f.read())

with open("src/templates/wrapper.cpp.j2", "r") as f:
    cpp_template = jinja2.Template(f.read())

with open("src/templates/serializers.h.j2", "r") as f:
    serializers_template = jinja2.Template(f.read())

with open("src/templates/CMakeLists.txt.j2", "r") as f:
    cmake_template = jinja2.Template(f.read())

if __name__ == "__main__":
    args = parser.parse_args()

    os.path.isdir(args.proto_dir) or parser.error(f"{args.proto_dir} is not a directory")
    (files, definitions) = utils.load_files(args.proto_dir)
    os.makedirs(os.path.join(args.output_dir, "proto"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "inc"), exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "src"), exist_ok=True)

    for (filename, (package, schema)) in files:
        print(f'Generating files for {filename}.proto...')
        with open(os.path.join(args.output_dir, f"{filename}.h"), "w") as f:
            f.write(h_template.render(file_elements=schema.file_elements, filename=filename, package=package, utils=utils, packages_definitions=definitions))
            print(f"✅ Generated header file {os.path.join(args.output_dir, f'{filename}.h')}")
        with open(os.path.join(args.output_dir, "src", f"{filename}.cpp"), "w") as f:
            f.write(cpp_template.render(file_elements=schema.file_elements, filename=filename, package=package, utils=utils))
            print(f"✅ Generated source file {os.path.join(args.output_dir, 'src', f'{filename}.cpp')}", end="\n\n")


    print(f"Generating header file...")
    with open(os.path.join(args.output_dir, "serializers.h"), "w") as f:
        f.write(serializers_template.render(filenames=list(map(lambda f: f[0], files))))
        print(f"✅ Generated header file {os.path.join(args.output_dir, 'serializers.h')}", end="\n\n")

    print(f"Generating file for CMake...")

    with open(os.path.join(args.output_dir, "CMakeLists.txt"), "w") as f:
        f.write(cmake_template.render(filenames=list(map(lambda f: f[0], files))))
        print(f"✅ Generated CMake file {os.path.join(args.output_dir, 'CMakeLists.txt')}", end="\n\n")

    print("Generated all files correctly!")
