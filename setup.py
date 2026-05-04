import sys
from sys import argv

if sys.platform.startswith("win"):
    runtypes = {
            "windows": ["run"],
        }
elif sys.platform.startswith("linux"):
    runtypes = {
            "linux": ["run", "dlls"],
            "windows": ["dlls"],
        }
else:
    raise OSError("Unsupported platform")

def help(program):
    print(f"{program}   windows {'|'.join(runtypes['windows'])}")
    print(f"{program}   linux   {'|'.join(runtypes['linux'])}")

if len(argv) != 3:
    help(argv[0])
    print("Error: Expected 3 arguments.")
    exit(1)

platforms=["windows", "linux"]
platform = argv[1].lower()

if not platform in platforms:
    help(argv[0])
    print(f"Error: Unknown '{platform}' platform. Wanted any of these: {', '.join(platforms)}.")
    exit(1)

runtype = argv[2].lower()
if not runtype in runtypes[platform]:
    help(argv[0])
    print(f"Error. Unknown '{runtype}' argument. Wanted any of these: {', '.join(runtypes[platform])}.")
    exit(1)

import os
if not os.path.exists("./libs"):
    os.makedirs("./libs")

import subprocess
def compileLinux():
    for _, _, files in os.walk("./algorithms"):
        for file in files:
            print(f"CC   {file}")
            platforms_compilers={
                    "linux": ["cc", "-shared", f"./algorithms/{file}", "-o", f"./libs/{file[:len(file)-1]}so", "-O3"],
                    "windows": ["x86_64-w64-mingw32-cc", 
                                "-shared", f"./algorithms/{file}",
                                "-o", f"./libs/{file[:len(file)-1]}dll", "-O3"],
                    }
            return_code = subprocess.call(platforms_compilers[platform])
            if return_code != 0:
                print(f"Error: Couldn't compile {file}. Returned code: {return_code}.")
                exit(1)
if sys.platform.startswith("win"):
    # TODO: Compile for windows
    pass
elif sys.platform.startswith("linux"):
    compileLinux()


if runtype == "run":
    import main
