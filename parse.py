import babeltrace
import sys
import statistics
import copy

class WorkEvent:
    def __init__(self, ts):
        self.timestamp = ts

class Work:
    def __init__(self):
        # map from name to event
        self.events = {}
        self.has_txn = False

    def __getitem__(self, key):
        return self.events[key]

    def __setitem__(self, key, value):
        self.events[key] = value

def get_avg_duration(works, before, after):
    return statistics.mean(w[after].timestamp - w[before].timestamp for w in works if w.has_txn)

def main():
    if len(sys.argv) != 2:
        msg = 'Usage: python3 {} TRACEPATH'.format(sys.argv[0])
        print(msg, file=sys.stderr)
        return

    # A trace collection contains one or more traces
    col = babeltrace.TraceCollection()

    # Add the trace provided by the user (LTTng traces always have
    # the 'ctf' format)
    if col.add_traces_recursive(sys.argv[1], 'ctf') is None:
        raise RuntimeError('Cannot add trace')

    works = []
    work = None
    for event in col.events:
        if event.name == "mongo:before_schedule_write_to_oplog":
            work = Work()

        work[event.name] = WorkEvent(event.timestamp)

        if event.name == "mongo:txn_apply":
            work.has_txn = True

        if event.name == "mongo:after_oplog_application":
            works.append(work)

    print("Total batches:", len(works))
    print("Total txn commit batches:", sum(1 for w in works if w.has_txn))

    event_durations = [
        ("mongo:before_schedule_write_to_oplog", "mongo:after_schedule_write_to_oplog"),
        ("mongo:after_schedule_write_to_oplog", "mongo:after_dispatch_writes"),
        ("mongo:after_schedule_write_to_oplog", "mongo:after_oplog_write"),
        ("mongo:after_oplog_write", "mongo:after_write_consistency_markers"),
        ("mongo:after_write_consistency_markers", "mongo:after_oplog_application"),
    ]

    txn_application_durations = [
        ("mongo:after_schedule_write_to_oplog", "mongo:start_commit_apply"),
        ("mongo:start_commit_apply", "mongo:start_read_from_oplog_chain"),
        ("mongo:start_read_from_oplog_chain", "mongo:start_traverse_iterater"),
        ("mongo:start_traverse_iterater", "mongo:start_reverse_oplog_from_disk"),
        ("mongo:start_reverse_oplog_from_disk", "mongo:start_build_cached_ops"),
        ("mongo:start_build_cached_ops", "mongo:end_build_cached_ops"),
        ("mongo:end_build_cached_ops", "mongo:txn_apply"),
    ]
    print("Time durations (in microseconds):")
    for before, after in event_durations:
        print("{:40}----->   {:40}".format(before, after), end = "")
        print("{:11.3f}".format(get_avg_duration(works, before, after)/1000))

    print()
    print("Time durations of transaction dispacth (in microseconds):")
    for before, after in txn_application_durations:
        print("{:40}----->   {:40}".format(before, after), end = "")
        print("{:11.3f}".format(get_avg_duration(works, before, after)/1000))

if __name__ == '__main__':
    main()
