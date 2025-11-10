import sys
from main import main_function

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python search.py <file_path> <method>")
        sys.exit(1)

    file_path = f"{sys.argv[1]}"
    method = sys.argv[2].upper()

    main_function(file_path, method)
