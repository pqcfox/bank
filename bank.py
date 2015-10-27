import abc
import random
import statistics

import customer
import settings
import times


class Bank(object):
    """A simple bank simulator."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, teller_count, line_count):
        self.teller_count = teller_count
        self.line_count = line_count

    @abc.abstractmethod
    def handle_arrival(self, lines, new_customer):
        """Determines which line an arrival should go to."""

    @abc.abstractmethod
    def handle_service(self, lines):
        """Determines which line should be served first."""

    def run(self, iterations, debug=False):
        line_lengths, wait_times = [], []
        for _ in range(iterations):
            line_length, wait_time = self.run_trial(debug)
            line_lengths.append(line_length)
            wait_times.append(wait_time)
        return statistics.mean(line_lengths), statistics.mean(wait_times)

    def run_trial(self, debug=False):
        """Runs a single trial of the bank."""
        lines, wait_times, line_lengths = [[] for _ in range(self.line_count)], [], []
        arrivals = times.file_times(settings.ARRIVAL_FILE) if debug else times.random_times(settings.ARRIVAL_PROBS)
        services = times.file_times(settings.SERVICE_FILE) if debug else times.random_times(settings.SERVICE_PROBS)
        current_time, arrival_time, service_times = 0, arrivals.__next__(), [0 for _ in range(self.teller_count)]

        in_service = [False for _ in range(self.teller_count)]
        customers_left = settings.DEBUG_EXAMPLES if debug else settings.CUSTOMER_COUNT

        def print_debug(tag, newline=False):
            """Prints debug information."""
            if debug: # REPAIR
                args = (lines, current_time, arrival_time, service_times, in_service, customers_left, tag)
                output = "{} CT:{} AT:{} ST:{} IS:{} CR:{} ({})".format(*args)
                output += "\n" if newline else ""
                print(output)

        # Keep iterating while we have customers entering, in line, or in service
        while customers_left > 0 or any([len(line) > 0 for line in lines]) or any(in_service):
            # Print debug information
            print_debug("start of time step")

            # If someone is being served, and their time is up, stop service
            for i in range(self.teller_count):
                if in_service[i] and service_times[i] <= current_time:
                    in_service[i] = False
                    for line in lines:
                        for i in range(len(line)):
                            line[i].line_length += 1

            # Print debug information
            print_debug("after finishing service")

            # If someone arrives, add them to a line and schedule another
            if arrival_time <= current_time and customers_left > 0:
                new_customer = customer.Customer(services.__next__())
                line_index = self.handle_arrival(lines, new_customer)
                lines[line_index].append(new_customer)
                customers_left -= 1
                # Ensure that we haven't run out of debug delays
                if customers_left != 0:
                    arrival_time = current_time + arrivals.__next__()
            # Print debug information
            print_debug("after adding new people")

            # If no one is being served, serve someone and start a timer
            for i in range(self.teller_count):
                if not in_service[i] and any([len(line) > 0 for line in lines]):
                    in_service[i] = True
                    line_index = self.handle_service(lines)
                    served_customer = lines[line_index].pop(0)
                    line_lengths.append(served_customer.line_length)
                    wait_times.append(served_customer.wait_time)
                    service_times[i] = current_time + served_customer.task_time

            # Print debug information
            print_debug("after starting new service")

            # If we're not in service or our service time is set in the future
            # and our arrival time is set in the future, step time forward
            service_ready = [not in_service[i] or service_times[i] > current_time for i in range(self.teller_count)]
            arrival_ready = (arrival_time > current_time or customers_left <= 0)
            if all(service_ready) and arrival_ready:
                current_time += 1
                for line in lines:
                    for i in range(len(line)):
                        line[i].wait_time += 1
            # Print debug information
            print_debug("after incrementing times", newline=True)

        # Print additional debug information
        if debug:
            print("Line lengths: {}".format(line_lengths))
            print("Wait times: {}".format(wait_times))

        return statistics.mean(line_lengths), statistics.mean(wait_times)


class SimpleBank(Bank):
    """A single line Bank."""
    def __init__(self, teller_count):
        self.teller_count = teller_count
        self.line_count = 1

    def __repr__(self):
        return "SimpleBank({})".format(self.teller_count)

    def handle_arrival(self, lines, new_customer):
        return 0

    def handle_service(self, lines):
        return 0


class PartitionBank(Bank):
    def __init__(self, teller_count, partitions):
        self.teller_count = teller_count
        self.partitions = partitions
        self.line_count = len(partitions)
        self.line_index = 0

    def __repr__(self):
        return "PartitionBank({}, {})".format(self.teller_count, self.partitions)

    def handle_arrival(self, lines, new_customer):
        available = []
        for i in range(len(self.partitions)):
            if new_customer.task_time in self.partitions[i]:
                available.append(i)
        return random.choice(available)

    def handle_service(self, lines):
        selected = False
        while not selected:
            self.line_index += 1
            self.line_index %= self.line_count
            selected = len(lines[self.line_index]) != 0
        return self.line_index
