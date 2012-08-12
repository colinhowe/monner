import argparse, multiprocessing, os, subprocess, sys
import psutil

KILOBYTES = 1024.0
MEGABYTES = KILOBYTES * 1024.0

def _get_cpu_stats():
    return psutil.cpu_percent(0)

def _get_memory_used():
    memory_used = psutil.phymem_usage().used - psutil.cached_phymem()
    return memory_used / MEGABYTES

_last_network_out = _last_network_in = 0
def _get_network_stats():
    global _last_network_in, _last_network_out
    network_stats = psutil.network_io_counters()
    
    network_in = network_stats.bytes_recv - _last_network_in
    network_in /= KILOBYTES
    _last_network_in = network_stats.bytes_recv

    network_out = network_stats.bytes_sent - _last_network_out
    network_out /= KILOBYTES
    _last_network_out = network_stats.bytes_sent

    return network_in, network_out

_calculations = (
    ('CPU (%)', _get_cpu_stats),
    ('Memory used (mb)', _get_memory_used),
    ('Network in (kb)', lambda: _get_network_stats()[0]),
    ('Network out (kb)', lambda: _get_network_stats()[1]),
)

def output_stats():
    stats = [('%.1f' % stat_fn()).rjust(len(name))
            for name, stat_fn in _calculations]
    print '\t'.join(stats)

def init_stats():
    _get_cpu_stats()
    _get_network_stats()

def print_header():
    print '\t'.join(name for name, _ in _calculations)

_kill_monitor = multiprocessing.Event()

def _monitor(interval):
    pid = os.fork()
    if pid != 0:
        return pid
    
    init_stats()

    try:
        while not _kill_monitor.wait(interval):
            output_stats()
    except KeyboardInterrupt:
        pass
    finally:
        output_stats()

def launch_monitor(interval):
    p = multiprocessing.Process(target=_monitor, args=(interval,))
    p.start()
    return p

def halt_monitor(monitor):
    _kill_monitor.set()
    monitor.join()

def run_target(target, target_args, target_output):
    try:
        subprocess.call([target] + target_args,
                stdout=target_output, stderr=target_output)
    except KeyboardInterrupt:
        pass

def go(target, target_args, target_output, interval):
    print_header()
    monitor = launch_monitor(interval)

    try:
        run_target(target, target_args, target_output)
    finally:
        halt_monitor(monitor)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Run a command and output system stats to a file')
    parser.add_argument('-i, --interval',
        dest='interval', help='Interval (seconds)', default=1, type=int)
    parser.add_argument('--target-output',
        help='Output file for target program',
        default=sys.stdout, type=argparse.FileType('wb', 0))

    parser.add_argument('command')
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    go(args.command, args.args, args.target_output,
            interval=args.interval)
