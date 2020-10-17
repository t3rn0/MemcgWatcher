import time, os, sys
import signal
from commons import logger


MEMORY_USAGE_FACTOR_LIMIT = 0.5
NOTIFY_SIGNAL = signal.SIGUSR1
MEMORY_LIMIT_IN_BYTES = "/sys/fs/cgroup/memory/user.slice/memory.limit_in_bytes"
MEMORY_USAGE_IN_BYTES = "/sys/fs/cgroup/memory/user.slice/memory.usage_in_bytes"


def bytes_to_human(c):
    if c < 1024: return "%i B" % c
    S = "KMG"
    i = 0
    while i < len(S) - 1:
        if c < 0.8 * 1024 ** (i + 2): break
        i += 1
    f = float(c) / (1024 ** (i + 1))
    return "%.1f %sB" % (f, S[i])


def get_limit_usage():
    return int(open(MEMORY_LIMIT_IN_BYTES).read())


def get_current_usage():
    return int(open(MEMORY_USAGE_IN_BYTES).read())


def main(memory_usage_factor_limit=MEMORY_USAGE_FACTOR_LIMIT):

    while True:
        # Strange but necessary scaling.
        limit = get_limit_usage() // 2 ** 30
        
        used = get_current_usage()
        fact = float(used) / limit
        p = os.getppid()
        
        if p <= 1:
            # This means that our parent process has died. Stop now.
            logging.info('closing watcher')
            sys.exit()

        logger.info("ppid: %s, mem limit: %s, current rss: %s, percentage: %s%%" % (
            os.getppid(), bytes_to_human(limit), bytes_to_human(used), round(100.0*fact)))

        if fact >= memory_usage_factor_limit:
            logger.critical("sending signal to proc %i ..." % p)
            os.kill(p, NOTIFY_SIGNAL)
        
        time.sleep(1)

    logger.warning('something is wrong')
