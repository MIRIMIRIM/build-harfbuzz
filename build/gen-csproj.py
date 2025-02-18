#!/usr/bin/env python3
import sys

base_lib_name = "libharfbuzz"
architectures = ["x64", "arm64"]
lib_types = ["static", "shared"]
runtime_template = "{prefix}-{arch}"
platforms = {
    "win": {
        "prefix": "win",
    },
    "linux": {
        "prefix": "linux-musl",
    },
    "mac": {
        "prefix": "osx",
    }
}

extension_map = {
    "win": {"static": ".a", "shared": ".dll"},
    "linux": {"static": ".a", "shared": ".so"},
    "mac": {"static": ".a", "shared": ".dylib"}
}

def generate_csproj_content(platform_key, lib_type):
    platform_info = platforms[platform_key]
    package_id = f"MIR.NativeLib.Harfbuzz.{lib_type.capitalize()}.{platform_key.capitalize()}"
    file_ext = extension_map[platform_key][lib_type]

    if platform_key == "win":
        # remove 'lib'
        base_lib_name2 = base_lib_name[3:]
    else:
        base_lib_name2 = base_lib_name
    
    none_entries = []
    for arch in architectures:
        runtime_dir = runtime_template.format(
            prefix=platform_info["prefix"],
            arch=arch,
        )
        runtime_bt_dir = runtime_dir + '-' + lib_type

        for lib in ["", "-subset"]:
            entry = (
                f'    <None Include="{runtime_bt_dir}\\src\\{base_lib_name2}{lib}{file_ext}" Pack="true" PackagePath="runtimes\\{runtime_dir}\\native" />'
            )
            none_entries.append(entry)
    
    none_items = "\n".join(none_entries)
    
    csproj_content = f'''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <PackageId>{package_id}</PackageId>
  </PropertyGroup>
  <ItemGroup>
{none_items}
  </ItemGroup>
  <Import Project="global.props" />
</Project>
'''
    return package_id, csproj_content

def gen_csproj(platform):
    for lib_type in lib_types:
        package_id, content = generate_csproj_content(platform, lib_type)
        filename = f"{package_id}.csproj"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Generate '{filename}'")

def main():
    if len(sys.argv) != 2:
        print("usage: {} <platform>".format(sys.argv[0]))
        print("platform options: win, linux, mac")
        sys.exit(1)
        
    platform_arg = sys.argv[1].lower()
    
    if platform_arg not in platforms and platform_arg != 'all':
        print(f"Unsupport platform: {platform_arg}. Optional value: {', '.join(platforms.keys())}")
        sys.exit(1)
    
    if platform_arg == 'all':
        for plat in platforms.keys():
            gen_csproj(plat)
    else:
        gen_csproj(platform_arg)

if __name__ == "__main__":
    main()
