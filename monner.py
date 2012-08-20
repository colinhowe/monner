import argparse, subprocess, sys, time
import psutil

KILOBYTES = 1024.0
MEGABYTES = KILOBYTES * 1024.0

def get_cpu_stats(pid):
    return psutil.cpu_percent(0)

get_mem = lambda pid: psutil.Process(pid).get_memory_info()
def get_mem_rss(pid):
    return get_mem(pid).rss / MEGABYTES

def get_mem_vms(pid):
    return get_mem(pid).vms / MEGABYTES

def counter(fn, field_name, divisor=1):
    def wrapper(pid):
        reading = getattr(fn(), field_name)
        change = reading - wrapper.last_reading
        wrapper.last_reading = reading
        return change / divisor
    wrapper.last_reading = 0
    return wrapper

get_network_in = counter(psutil.network_io_counters, 'bytes_recv', KILOBYTES)
get_network_out = counter(psutil.network_io_counters, 'bytes_sent', KILOBYTES)

get_disk_in = counter(psutil.disk_io_counters, 'read_bytes', KILOBYTES)
get_disk_out = counter(psutil.disk_io_counters, 'write_bytes', KILOBYTES)

_calculations = {
    'system_cpu': ('CPU (%)', get_cpu_stats),
    'process_rss': ('Memory RSS (mb)', get_mem_rss),
    'process_vms': ('Memory VMS (mb)', get_mem_vms),
    'system_network_in': ('Network in (kb)', get_network_in),
    'system_network_out': ('Network out (kb)', get_network_out),
    'system_disk_in': ('Disk in (kb)', get_disk_in),
    'system_disk_out': ('Disk out (kb)', get_disk_out),
}

def gather_stats(pid, fields):
    for field in fields:
        name, fn = _calculations[field]
        yield name, fn(pid)

def output_stats(pid, fields):
    stats = [('%.1f' % value).rjust(len(name))
            for name, value in gather_stats(pid, fields)]
    print '\t'.join(stats)

def init_stats(pid):
    for _, fn in _calculations.itervalues():
        fn(pid)

def print_header(fields):
    print '\t'.join(_calculations[field][0] for field in fields)

def run_target(target, target_output):
    return subprocess.Popen(target,
            stdout=target_output, stderr=target_output)

def go(target, target_output, interval, fields):
    print_header(fields)
    target = run_target(target, target_output)

    init_stats(target.pid)
    while True:
        time.sleep(interval)
        output_stats(target.pid, fields)
        if target.poll() is not None:
            break

field_help = '''
All fields are prefixed with either system or process to indicate whether they
are the stats for just the process or are the system as a whole.

system_cpu
    average CPU usage as a percentage

process_rss, process_vms
    Memory: RSS, VMS in MB

system_network_in, system_network_out
    Network: inbound/outbound bandwidth usage in KB

system_disk_in, system_disk_out
    Disk: reads/writes to disk in KB
'''

default_fields = [
    'system_cpu', 'process_rss', 'system_network_in', 'system_network_out',
    'system_disk_in', 'system_disk_out',
]

def main():
    epilog = field_help

    parser = argparse.ArgumentParser(
            description='Run a command and output system stats to a file',
            epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--interval',
        dest='interval', help='Interval (seconds)', default=1, type=int)
    parser.add_argument('--target-output',
        help='Output file for target program',
        default=sys.stdout, type=argparse.FileType('wb', 0))
    parser.add_argument('-f', '--fields',
        help='Fields to display.', nargs='*',
        default=default_fields, choices=_calculations.keys())
    parser.add_argument('command', nargs='+',
        help='Command to run, including arguments')

    args = parser.parse_args()
    go(args.command, args.target_output,
            interval=args.interval, fields=args.fields)

if __name__ == '__main__':
    main()
