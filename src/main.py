import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(Path(__file__).parent.parent / "log" / "app.log")
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def add_func(x: int | float, y: int | float) -> int | float:
    return x + y


def multiply(a: int | float, b: int | float) -> int | float:
    return a * b


def show_data(df: pd.DataFrame) -> None:
    print(df)


def main() -> int:
    env_path = Path(__file__).parent.parent / ".env"
    # logger.info(f"Looking for .env at: {env_path}")  # add this
    # logger.info(f"File exists: {env_path.exists()}")  # add this
    load_dotenv(env_path, override=True)
    passwd = os.getenv("PASSWORD")

    if passwd is None:
        logger.error("PASSWORD environment variable not set")
        raise OSError("PASSWORD environment variable not set")
    else:
        logger.info("Password loaded")

    df = pd.DataFrame(np.array(range(1, 10)).reshape(3, 3))

    data = {
        "Name": ["Martha", "Tim", "Rob", "Georgia"],
        "Maths": [87, 91, 97, 95],
        "Science": [83, 99, 84, 76],
    }
    df2 = pd.DataFrame(data)

    logger.info("Second dataframe created")
    logger.info(add_func(2, 3))
    logger.info(df)
    logger.info(df2)

    return 0


if __name__ == "__main__":
    main()
