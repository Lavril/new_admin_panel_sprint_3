import logging
import os.path

from etl import run_etl

if __name__ == '__main__':
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    logging.basicConfig(level=logging.INFO, filename="logs/etl.log", filemode="w",
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")

    run_etl()
