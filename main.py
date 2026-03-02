import subprocess
from src.ruff_test import add_func
from src.ruff_test import multiply

def main():
    print("Hello from python-pro-dev!")

    # run python script at src folder
    subprocess.run(["python", "src/ruff_test.py"])


if __name__ == "__main__":
    main()
