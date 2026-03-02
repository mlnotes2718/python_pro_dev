import subprocess

def main():
    print("Hello from python-pro-dev!")

    # run python script at src folder
    subprocess.run(["python", "src/ruff_test.py"])


if __name__ == "__main__":
    main()
