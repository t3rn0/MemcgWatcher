import signal
import os
import memcg_watcher
import multiprocessing
from commons import logger, OutOfMemoryError


def signal_handler(signum, frame):
    logger.critical(f'got signum {signum}, handling')
    if signum == 2:
        raise KeyboardInterrupt
    raise OutOfMemoryError


signal.signal(signal.SIGUSR1, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGCHLD, signal_handler)


def expensive_work():
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
        expensive_work()
    except OutOfMemoryError:
        logger.critical(f'catched OutOfMemoryError, closing...')
    finally:
        shutdown()


if __name__ == '__main__':
    import platform
    if platform.system() != 'Linux':
        raise EnvironmentError
    
    pid = os.getpid()
    params = {
        'memory_usage_factor_limit': 0.5,
    }

    subprocess = multiprocessing.Process(
        target=memcg_watcher.main, args=(pid,), kwargs=params, daemon=True
    )

    try:
        subprocess.start()
        main()
    finally:
        subprocess.terminate()
