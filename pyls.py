import argparse
import json
import os
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description="Python ls implementation")
    parser.add_argument("-A", "--all", action="store_true", help="do not ignore entries starting with .")
    parser.add_argument("-l", "--long", action="store_true", help="use a long listing format")
    parser.add_argument("-r", "--reverse", action="store_true", help="reverse order while sorting")
    parser.add_argument("-t", "--time", action="store_true", help="sort by modification time, newest first")
    parser.add_argument("--filter", choices=["file", "dir"], help="filter output by file or directory")
    parser.add_argument("-H", "--human-readable", action="store_true", help="show human-readable file sizes")
    parser.add_argument("path", nargs="?", default=".", help="directory or file to list")
  
    return parser.parse_args()

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

    ### Step 2: Helper Functions  

    def is_hidden(name):
        return name.startswith('.')

    def format_size(size, human_readable=False):
        if not human_readable:
            return str(size)
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024

    def format_time(epoch_time):
        return time.strftime("%b %d %H:%M", time.localtime(epoch_time))

    ### Step 3: Handling File and Directory Listing

    def list_directory(directory, show_all, long_format, reverse, sort_time, filter_type, human_readable):
        items = directory.get('contents', [])

        # Filter hidden files if `show_all` is False
        if not show_all:
            items = [item for item in items if not is_hidden(item['name'])]

        
        # Sort by time or name
        if sort_time:
            items.sort(key=lambda x: x['time_modified'], reverse=not reverse)
        else:
            items.sort(key=lambda x: x['name'], reverse=reverse)

        # Print in long format or short format
        for item in items:
            if long_format:
                size = format_size(item['size'], human_readable)
                mod_time = format_time(item['time_modified'])
                print(f"{item['permissions']} {size} {mod_time} {item['name']}")
            else:
                print(item['name'], end=" ")
        if not long_format:
            print()
    ### Step 4: Path Navigation and Error Handling

    def navigate_path(directory, path):
        if path == ".":
            return directory

        parts = path.split('/')
        current_dir = directory

        for part in parts:
            for item in current_dir.get('contents', []):
                if item['name'] == part and 'contents' in item:
                    current_dir = item
                    break
            else:
                print(f"error: cannot access '{path}': No such file or directory")
                return None
        return current_dir

    ### Step 5: Bringing It All Together

    def main():
        args = parse_arguments()

        # Load the JSON file
        directory_structure = load_json('structure.json')

        # Navigate to the specified path
        current_dir = navigate_path(directory_structure, args.path)

        if current_dir:
            list_directory(
                current_dir,
                show_all=args.all,
                long_format=args.long,
                reverse=args.reverse,
                sort_time=args.time,
                filter_type=args.filter,
                human_readable=args.human_readable
            )

    if __name__ == "__main__":
        main()
