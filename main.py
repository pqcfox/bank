import itertools
import random

import bank
import settings

TELLER_COUNT = 1
PARTITION_FRACTION = 0.001
FIRST_ITERATIONS = 100
SECOND_ITERATIONS = 10000
DEBUG = False

queue_lengths = {}
wait_times = {}
baseline_bank = bank.SimpleBank(teller_count=TELLER_COUNT)
banks = []

possible_banks = []
if not DEBUG:
    task_times = settings.SERVICE_PROBS.keys()
    possible_partitions = []
    for r in range(1, len(task_times) + 1):
        for p in itertools.combinations(task_times, r):
            possible_partitions.append(p)

    partition_sets = []
    for line_count in range(2, len(task_times) + 1):
        for partitions in itertools.product(possible_partitions, repeat=line_count):
            flat_partitions = [task for partition in partitions for task in partition]
            if all([t in flat_partitions for t in task_times]):
                partition_sets.append(partitions)

    for partitions in random.sample(partition_sets, int(PARTITION_FRACTION * len(partition_sets))):
        banks.append(bank.PartitionBank(teller_count=TELLER_COUNT, partitions=partitions))

iterations = 1 if DEBUG else FIRST_ITERATIONS
base_queue_length, base_wait_time = baseline_bank.run(debug=DEBUG, iterations=iterations)
passing_banks = []

for b in banks:
    queue_length, wait_time = b.run(debug=DEBUG, iterations=iterations)
    if queue_length < base_queue_length and wait_time < base_wait_time:
        passing_banks.append(b)
        queue_lengths[b] = queue_length
        wait_times[b] = wait_time

if not DEBUG:
    print("{} candidates found.".format(len(queue_lengths)))
    # Use product of margins as heuristic
    heuristic = lambda b: (base_queue_length - queue_lengths[b]) * (base_wait_time - wait_times[b])
    selected = min(passing_banks, key=heuristic)
    print("Top candidate: {}".format(selected))
    large_base_queue_length, large_base_wait_time = baseline_bank.run(iterations=SECOND_ITERATIONS)
    large_queue_length, large_wait_time = selected.run(iterations=SECOND_ITERATIONS)
    print("Mean baseline queue length and wait time: {}, {}".format(large_base_queue_length, large_base_wait_time))
    print("Mean optimized queue length and wait time: {}, {}".format(large_queue_length, large_wait_time))