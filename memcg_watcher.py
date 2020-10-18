from commons import logger
import linuxfd
import select
import platform


if platform.system() != 'Linux':
    raise EnvironmentError


MEMORY_USAGE_FACTOR_LIMIT = 0.5
MEMORY_LIMIT_IN_BYTES = "/sys/fs/cgroup/memory/memory.limit_in_bytes"
MEMORY_USAGE_IN_BYTES = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
CGROUP_EVENT_CONTROL = "/sys/fs/cgroup/memory/cgroup.event_control"


def get_limit_usage():
    return int(open(MEMORY_LIMIT_IN_BYTES).read())


def get_current_usage():
    return int(open(MEMORY_USAGE_IN_BYTES).read())


def get_threshold(factor):
    # Strange but necessary scaling
    limit = get_limit_usage() // 2 ** 30
    return int(limit * factor)


def main(memory_usage_factor_limit=MEMORY_USAGE_FACTOR_LIMIT):
    name = 'MemWatcher'
    logger.info(f'starting {name}')

    efd = linuxfd.eventfd(initval=0, nonBlocking=True)
    mfd = open(MEMORY_USAGE_IN_BYTES)
    mfd.fileno()
    threshold = get_threshold(memory_usage_factor_limit)

    with open(CGROUP_EVENT_CONTROL, 'w') as f:
        f.write(f'{efd.fileno()} {mfd.fileno()} {threshold}')

    epl = select.epoll()
    epl.register(efd.fileno(), select.EPOLLIN)

    try:
        isrunning = True
        while isrunning:
            events = epl.poll(-1)
            for fd, event in events:
                if fd == efd.fileno() and event & select.EPOLLIN:
                    logger.info('event file received update')
                    logger.info(f'{name} sent signal to the main process')
                    efd.read()
                    isrunning = False
    finally:
        logger.info(f'closing {name}')
        epl.unregister(efd.fileno())
        epl.close()
