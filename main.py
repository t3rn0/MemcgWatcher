import signal
import os
import multiprocessing
import memcg_watcher
from commons import logger, OutOfMemoryError
import sys


def signal_handler(signum, frame):
    logger.critical(f'got signum {signum}, handling')
    raise OutOfMemoryError()


signal.signal(signal.SIGUSR1, signal_handler)


def expernsive_function():
    ttt = []
    i = 0
    while True:
        ttt.append(i)
        i += 1


def shutdown():
    logger.info('shutting down main process')


def main():
    p = os.getpid()
    logger.info(f'main function started with pid {p}')
    try:
        expernsive_function()
    except OutOfMemoryError as e:
        logger.critical(f'catched OutOfMemoryError, closing...', exc_info=True)
    finally:
        shutdown()


if __name__ == '__main__':
    memcg_parameters = {
        'memory_usage_factor_limit': 0.8,
    }
    
    subprocess = multiprocessing.Process(
        target=memcg_watcher.main, name='memcg_watcher', 
        kwargs=memcg_parameters, 
        daemon=True
    )
    subprocess.start()

    main()
