from core.AFL import AFL
from core.AFS import AFS
from colorama import Fore, Style
import core.utils as ut
import os, sys
import argparse
import time
from core.STPZ_LZ import *

if __name__ == "__main__":
    ut.clear_temp_dir()

    parser = argparse.ArgumentParser(description='AFS Builder v0.1')
    parser.add_argument('-afl', '--afl', nargs='?', help="AFL path")
    parser.add_argument('-b', '--build', nargs='?', help="Input folder to repack")
    parser.add_argument('-c', '--compress', nargs='?', help="Compress files when repacking (default: False)")
    parser.add_argument('-d', '--decompress', nargs='?', help="Decompress files when extracting (default: False)")
    parser.add_argument('-f', '--force', nargs='?', help="Bypass file/folder overwrite warning (default: False)")
    parser.add_argument('-g', '--game', nargs='?', help="Target game (dbrb/dbut) (default: dbrb)")
    parser.add_argument('-l', '--list', nargs='?', help="List files in archive")
    parser.add_argument('-o', '--output', nargs='?', help="Output path")
    parser.add_argument('-u', '--update', nargs='?', help="Update archive")
    parser.add_argument('-x', '--extract', nargs='?', help="Input file to extract")
    parser.set_defaults(compress="False", decompress="False", force="False", game="dbrb")
    args = parser.parse_args()

    cm.selected_game = args.game

    output_path = None
    if (args.output != None):
        output_path = args.output

    if (args.list != None):
        stream = open(args.list, 'rb')
        afs_object = AFS()
        afs_object.read(stream)
        for entry in afs_object.entries:
            print(f'{entry.size:14} Bytes - {entry.name}')
        if (args.afl):
            afl_path = args.afl
            print(f"{Fore.GREEN}Output AFL path: {afl_path}{Style.RESET_ALL}")
            print(f"Saving AFL file...")

            if (args.force == "True"):
                if (os.path.exists(afl_path)):
                    print(f"{Fore.RED}ERROR: AFL file already exists (use -f to force overwrite).{Style.RESET_ALL}")
                    exit(1)

            ut.make_parent_dirs(afl_path)
            stream = open(afl_path, 'wb')
            afs_object.save_AFL(stream)
    elif (args.extract != None):
        input_name = os.path.basename(args.extract)
        name, ext = os.path.splitext(input_name)
        stream = open(args.extract, 'rb')
        afs_object = AFS()

        start = time.time()
        print(f"Reading files in archive...")
        afs_object.read(stream)

        if (output_path == None):
            output_path = os.path.join(os.getcwd(), name)
            print(f"{Fore.YELLOW}WARNING: No output folder specified, extracting in current folder.{Style.RESET_ALL}")
        if (not os.path.exists(output_path)):
            os.mkdir(output_path)

        print(f"{Fore.GREEN}Output path: {output_path}{Style.RESET_ALL}")

        if (args.force == "True"):
            if (os.path.exists(output_path) and (len(os.listdir(output_path)) > 0)):
                print(f"{Fore.RED}ERROR: Output folder already exists and is not empty (use -f to force overwrite).{Style.RESET_ALL}")
                exit(1)

        if (args.decompress == "True"):
            print(f"Decompressing files...")
            afs_object.decompress()
        ut.make_parent_dirs(output_path)
        afs_object.save(output_path)
        end = time.time()
        print(f"{len(afs_object.entries)} entries extracted in {round(end - start, 2)} seconds")
    elif (args.build != None):
        print(f"{Fore.GREEN}Input folder path: {args.build}{Style.RESET_ALL}")
        if (not os.path.exists(args.build)):
            print(f"{Fore.RED}ERROR: Input folder not found.{Style.RESET_ALL}")
            exit(1)

        input_name = os.path.basename(args.build)
        name = input_name + ".afs"
        afs_object = AFS(name)

        start = time.time()
        print(f"Loading files...")
        afs_object.load(args.build)

        if (output_path == None):
            output_path = os.path.join(os.getcwd(), name)
            print(f"{Fore.YELLOW}WARNING: No output file specified, output will be saved in current folder.{Style.RESET_ALL}")

        print(f"{Fore.GREEN}Output path: {output_path}{Style.RESET_ALL}")

        if (args.force != None):
            if (os.path.exists(output_path)):
                print(f"{Fore.RED}ERROR: Output file already exists (use -f to force overwrite).{Style.RESET_ALL}")
                exit(1)

        if (args.compress == "True"):
            print(f"Compressing files...")
            afs_object.compress()

        ut.make_parent_dirs(output_path)
        stream = open(output_path, "wb")
        afs_object.write(stream)
        end = time.time()
        print(f"{len(afs_object.entries)} files repacked in {round(end - start, 2)} seconds")
    elif (args.update != None):
        stream = open(args.update, 'rb')
        name = os.path.basename(args.update)
        afs_object = AFS(name)
        afs_object.read(stream)

        if (output_path == None):
            output_path = os.path.join(os.getcwd(), name)
            print(f"{Fore.YELLOW}WARNING: No output file specified, output will be saved in current folder.{Style.RESET_ALL}")

        if (args.afl):
            afl_path = args.afl
            print(f"Updating AFS file...")
            print(f"{Fore.GREEN}Input AFL path: {afl_path}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Output path: {output_path}{Style.RESET_ALL}")

            afl_object = AFL()
            ut.make_parent_dirs(afl_path)
            stream = open(afl_path, 'rb')
            afl_object.read(stream)

            if (len(afl_object.entries) != len(afs_object.entries)):
                print(f"{Fore.RED}ERROR: Entry count mismatch between provided AFL and AFS file.{Style.RESET_ALL}")
                exit(1)

            for i in range(len(afs_object.entries)):
                afs_object.entries[i].name = afl_object.entries[i]

            ut.make_parent_dirs(output_path)
            stream = open(output_path, 'wb')
            afs_object.write(stream)
    else:
        parser.print_help()