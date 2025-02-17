#!/usr/bin/env python3
import sys
import subprocess

scripts_path = "../scripts/"
project_file = f"{scripts_path}project.ini"
zig_conf_file = f"{scripts_path}zig.ini"
build_dir = "../build/{runtime}-{lib_type}"
runtime_conf = "{scripts_path}{runtime}.ini"

native_runtime = ['win-x64', 'osx-arm64']

architectures = ["x64", "arm64"]
lib_types = ["static", "shared"]
runtime_template = "{prefix}-{arch}"
platforms = {
    "win": {
        "prefix": "win",
        "args": ["-Db_vscrt=static_from_buildtype"]
    },
    "linux": {
        "prefix": "linux-musl",
        "args": ["--native-file", zig_conf_file, "--cross-file", zig_conf_file]
    },
    "mac": {
        "prefix": "osx",
        "args": []
    }
}

runtimes = [runtime_template.format(prefix=platforms[p]["prefix"], arch=arch) for p in platforms for arch in architectures]

def get_configure_command_args(runtime, lib_type):

    platform = runtime.rsplit('-', 1)[0]
    special_args = [p['args'] for p in platforms.values() if p['prefix'] == platform][0]

    args = ["meson"]

    if len(special_args) != 0:
        args += special_args

    if runtime in native_runtime:
        args += ['--native-file']
    else:
        args += ['--cross-file']
    args += [project_file]

    if runtime not in native_runtime:
        args += ['--cross-file', runtime_conf.format(scripts_path = scripts_path, runtime = runtime)]

    if lib_type == 'static':
        args += ['-Ddefault_library=static']

    args += [build_dir.format(runtime = runtime, lib_type = lib_type)]
    
    return args

def execute(runtime, lib_type):
    configure_args = get_configure_command_args(runtime, lib_type)
    print(" ".join(configure_args))
    subprocess.run(configure_args, check=True)

    compile_command_args = ["meson", "compile", "-C", configure_args[-1]]
    print(" ".join(compile_command_args))
    subprocess.run(compile_command_args, check=True)

def main():
    if len(sys.argv) != 3:
        print("usage: {} <runtime> <lib_type>".format(sys.argv[0]))
        print(f"runtime options: {', '.join(runtimes)}")
        print("lib_type options: static, shared")
        sys.exit(1)
    
    runtime_arg = sys.argv[1].lower()
    lib_type_arg = sys.argv[2].lower()

    if runtime_arg not in runtimes:
        print(f"Unsupport platform: {runtime_arg}. Optional value: {', '.join(runtimes)}")
        sys.exit(1)
    if lib_type_arg not in lib_types and lib_type_arg != 'all':
        print(f"Unsupport lib_type: {lib_type_arg}. Optional value: all, {', '.join(lib_types)}")
        sys.exit(1)
    
    if lib_type_arg == 'all':
        for t in lib_types:
            execute(runtime_arg, t)
    else:
        execute(runtime_arg, lib_type_arg)

if __name__ == "__main__":
    main()
