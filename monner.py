import argparse, subprocess, sys, time
import psutil

KILOBYTES = 1024.0
MEGABYTES = KILOBYTES * 1024.0

def _get_cpu_stats():
    return psutil.cpu_percent(0)

def _get_memory_used():
    memory_used = psutil.phymem_usage().used - psutil.cached_phymem()
    return memory_used / MEGABYTES

def _counter(fn, field_name, divisor=1):
    def wrapper():
        reading = getattr(fn(), field_name)
        change = reading - wrapper.last_reading
        wrapper.last_reading = reading
        return change / divisor
    wrapper.last_reading = 0
    return wrapper

_get_network_in = _counter(psutil.network_io_counters, 'bytes_recv', KILOBYTES)
_get_network_out = _counter(psutil.network_io_counters, 'bytes_sent', KILOBYTES)

_get_disk_in = _counter(psutil.disk_io_counters, 'read_bytes', KILOBYTES)
_get_disk_out = _counter(psutil.disk_io_counters, 'write_bytes', KILOBYTES)

_calculations = (
    ('CPU (%)', _get_cpu_stats),
    ('Memory used (mb)', _get_memory_used),
    ('Network in (kb)', _get_network_in),
    ('Network out (kb)', _get_network_out),
    ('Disk in (kb)', _get_disk_in),
    ('Disk out (kb)', _get_disk_out),
)

def output_stats():
    stats = [('%.1f' % stat_fn()).rjust(len(name))
            for name, stat_fn in _calculations]
    print '\t'.join(stats)

def init_stats():
    for _, fn in _calculations:
        fn()

def print_header():
    print '\t'.join(name for name, _ in _calculations)

def run_target(target, target_args, target_output):
    return subprocess.Popen([target] + target_args,
            stdout=target_output, stderr=target_output)

def go(target, target_args, target_output, interval):
    print_header()
    init_stats()
    target = run_target(target, target_args, target_output)

    while True:
        time.sleep(interval)
        output_stats()
        if target.poll() is not None:
            break

def main():
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

if __name__ == '__main__':
    main()
