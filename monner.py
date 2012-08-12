import argparse, subprocess, sys, time
import psutil

KILOBYTES = 1024.0
MEGABYTES = KILOBYTES * 1024.0

def _get_cpu_stats(pid):
    return psutil.cpu_percent(0)

_get_mem = lambda pid: psutil.Process(pid).get_memory_info()
def _get_mem_rss(pid):
    return _get_mem(pid).rss / MEGABYTES

def _get_mem_vms(pid):
    return _get_mem(pid).vms / MEGABYTES

def _counter(fn, field_name, divisor=1):
    def wrapper(pid):
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
    ('Memory RSS (mb)', _get_mem_rss),
    ('Memory VMS (mb)', _get_mem_vms),
    ('Network in (kb)', _get_network_in),
    ('Network out (kb)', _get_network_out),
    ('Disk in (kb)', _get_disk_in),
    ('Disk out (kb)', _get_disk_out),
)

def output_stats(pid):
    stats = [('%.1f' % stat_fn(pid)).rjust(len(name))
            for name, stat_fn in _calculations]
    print '\t'.join(stats)

def init_stats(pid):
    for _, fn in _calculations:
        fn(pid)

def print_header():
    print '\t'.join(name for name, _ in _calculations)

def run_target(target, target_args, target_output):
    return subprocess.Popen([target] + target_args,
            stdout=target_output, stderr=target_output)

def go(target, target_args, target_output, interval):
    print_header()
    target = run_target(target, target_args, target_output)

    init_stats(target.pid)
    while True:
        time.sleep(interval)
        output_stats(target.pid)
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
