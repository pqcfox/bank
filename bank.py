import abc
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
    def handle_arrival(self, lines):
        """Determines which line an arrival should go to."""

    @abc.abstractmethod
    def handle_service(self, lines):
        """Determines which line should be served first."""

    def run(self, debug=False):
        """Runs a single trial of the bank."""
        lines, wait_times, line_lengths = [[] for _ in range(self.line_count)], [], []
        arrivals = times.file_times(settings.ARRIVAL_FILE) if debug else times.random_times(settings.ARRIVAL_PROBS)
        services = times.file_times(settings.SERVICE_FILE) if debug else times.random_times(settings.SERVICE_PROBS)
        current_time, arrival_time, service_times = 0, arrivals.__next__(), [0 for _ in range(self.teller_count)]

        lines_to_count = []
        in_service = [False for _ in range(self.teller_count)]
        customers_left = 150 if debug is None else settings.DEBUG_EXAMPLES

        def print_debug(tag, newline=False):
            """Prints debug information."""
            if debug:
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
            # Print debug information
            print_debug("after finishing service")

            # If someone arrives, add them to a line and schedule another
            if arrival_time <= current_time and customers_left > 0:
                line_index = self.handle_arrival(lines)
                lines[line_index].append(customer.Customer(services.__next__()))
                customers_left -= 1
                lines_to_count.append(line_index)
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
                    wait_times.append(served_customer.wait_time)
                    service_times[i] = current_time + served_customer.task_time

            # Record line length if someone just arrived
            for line_index in lines_to_count:
                line_lengths.append(len(lines[line_index]))
            lines_to_count = []

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
                        line[i].step()
            # Print debug information
            print_debug("after incrementing times", newline=True)

        # Print additional debug information
        if debug:
            print("Queue lengths: {}".format(line_lengths))
            print("Wait times: {}".format(wait_times))

        return statistics.mean(line_lengths), statistics.mean(wait_times)


class SimpleBank(Bank):
    """A single line Bank."""
    def __init__(self, teller_count):
        self.teller_count = teller_count
        self.line_count = 1

    def handle_arrival(self, lines):
        return 0

    def handle_service(self, lines):
        return 0