import statistics

import bank

TELLER_COUNT = 1
ITERATIONS = 50000
DEBUG = True
DEBUG_FILES = {'arrival': 'debug_arrival_times.txt',
               'service': 'debug_service_times.txt'}

run_queue_lengths = []
run_wait_times = []
bank = bank.SimpleBank(teller_count=TELLER_COUNT)
for _ in range(1 if DEBUG else ITERATIONS):
    run_queue_length, run_wait_time = bank.run(debug=DEBUG)
    run_queue_lengths.append(run_queue_length)
    run_wait_times.append(run_wait_time)

print("Average queue length: {}".format(statistics.mean(run_queue_lengths)))
print("Average wait time: {}".format(statistics.mean(run_wait_times)))