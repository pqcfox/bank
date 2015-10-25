import random

TELLER_COUNT = 2
ITERATIONS = 50000
DEBUG = False
DEBUG_FILES = {'arrival': 'debug_arrival_times.txt',
               'service': 'debug_service_times.txt'}


def average(l):
    """Calculates the arithmetic mean of a list."""
    if len(l) == 0:
        raise ValueError('Cannot average an empty list')
    return sum(l)/len(l)


def weighted_random(p):
    """Selects a key at random with the paired value as the probability."""
    if sum(p.values()) != 1:
        raise ValueError('Probabilities must sum to unity')
    r = random.random()
    remaining = 1
    for category, probability in p.items():
        remaining -= probability
        if remaining <= r:
            return category


def integer_parse(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
        return [int(line) for line in lines]


def run_trial(teller_count, debug_times=None):
    """Runs a trial of the bank problem."""
    queue = []
    wait_times = []
    queue_lengths = []

    current_time = 0
    arrival_time = 0
    service_time = [0 for _ in range(teller_count)]
    update_queue_lengths = False
    in_service = [False for _ in range(teller_count)]

    customers_left = 150 if debug_times is None else len(debug_times['arrival'])
    arrival_prob = {0: 0.1, 1: 0.15, 2: 0.1, 3: 0.35, 4: 0.25, 5: 0.05}
    service_prob = {1: 0.25, 2: 0.2, 3: 0.4, 4: 0.15}
    probs = {'arrival': arrival_prob, 'service': service_prob}

    # Ensure that lists in debug_times are of equal length
    if debug_times is not None and len(debug_times['arrival']) != len(debug_times['service']):
        raise ValueError('Arrival and service debug times must have equal lengths')

    def print_debug(tag, newline=False):
        """Prints debug information."""
        if debug_times is not None:
            args = (queue, current_time, arrival_time, service_time, in_service, customers_left, tag)
            output = "{} CT:{} AT:{} ST:{} IS:{} CR:{} ({})".format(*args)
            output += "\n" if newline else ""
            print(output)

    def get_delay(label):
        """Gets a delay value."""
        if debug_times is None:
            return weighted_random(probs[label])
        else:
            return debug_times[label].pop(0)

    # Ensure that the first customer doesn't immediately show up
    arrival_time += get_delay('arrival')

    # Keep iterating while we have customers entering, in line, or in service
    while customers_left > 0 or len(queue) > 0 or any(in_service):
        # Print debug information
        print_debug("start of time step")

        # If someone is being served, and their time is up, stop service
        for i in range(teller_count):
            if in_service[i] and service_time[i] <= current_time:
                in_service[i] = False

        # Print debug information
        print_debug("after finishing service")

        # If someone arrives, add them to the queue and schedule another
        if arrival_time <= current_time and customers_left > 0:
            queue.append(0)
            customers_left -= 1
            update_queue_lengths = True
            # Ensure that we haven't run out of debug delays
            if customers_left != 0:
                arrival_time = current_time + get_delay('arrival')

        # Print debug information
        print_debug("after adding new people")

        # If no one is being served, serve someone and start a timer
        for i in range(teller_count):
            if not in_service[i] and len(queue) > 0:
                in_service[i] = True
                wait_times.append(queue.pop(0))
                service_time[i] = current_time + get_delay('service')

        # Record the queue length if someone just arrived
        if update_queue_lengths:
            queue_lengths.append(len(queue))
            update_queue_lengths = False

        # Print debug information
        print_debug("after starting new service")

        # If we're not in service or our service time is set in the future
        # and our arrival time is set in the future, step time forward
        service_ready = [not in_service[i] or service_time[i] > current_time for i in range(teller_count)]
        arrival_ready = (arrival_time > current_time or customers_left <= 0)
        if all(service_ready) and arrival_ready:
            current_time += 1
            for i in range(len(queue)):
                queue[i] += 1

        # Print debug information
        print_debug("after incrementing times", newline=True)

    # Print additional debug information
    if debug_times is not None:
        print("Queue lengths: {}".format(queue_lengths))
        print("Wait times: {}".format(wait_times))

    return average(queue_lengths), average(wait_times)


times = {label: integer_parse(filename) for label, filename in DEBUG_FILES.items()} if DEBUG else None
run_queue_lengths = []
run_wait_times = []
for _ in range(1 if DEBUG else ITERATIONS):
    run_queue_length, run_wait_time = run_trial(TELLER_COUNT, debug_times=times)
    run_queue_lengths.append(run_queue_length)
    run_wait_times.append(run_wait_time)

print("Average queue length: {}".format(average(run_queue_lengths)))
print("Average wait time: {}".format(average(run_wait_times)))