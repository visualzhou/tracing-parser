# tracing-parser

Exmaple output:

```
$ python3 parse.py ~/lttng-traces/big-txn-20190329-003615/
Total batches: 231
Total txn commit batches: 41
Time durations (in microseconds):
mongo:before_schedule_write_to_oplog    ----->   mongo:after_schedule_write_to_oplog         517.202
mongo:after_schedule_write_to_oplog     ----->   mongo:after_dispatch_writes             1035709.934
mongo:after_schedule_write_to_oplog     ----->   mongo:after_oplog_write                 1035712.065
mongo:after_oplog_write                 ----->   mongo:after_write_consistency_markers       447.825
mongo:after_write_consistency_markers   ----->   mongo:after_oplog_application             61773.075

Time durations of transaction dispacth (in microseconds):
mongo:after_schedule_write_to_oplog     ----->   mongo:start_commit_apply                  97976.501
mongo:start_commit_apply                ----->   mongo:start_read_from_oplog_chain            30.839
mongo:start_read_from_oplog_chain       ----->   mongo:start_traverse_iterater                13.722
mongo:start_traverse_iterater           ----->   mongo:start_reverse_oplog_from_disk      928636.529
mongo:start_reverse_oplog_from_disk     ----->   mongo:start_build_cached_ops                629.411
mongo:start_build_cached_ops            ----->   mongo:end_build_cached_ops                 3940.999
mongo:end_build_cached_ops              ----->   mongo:txn_apply                              48.573
```
