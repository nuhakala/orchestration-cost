import os
import time


class StatWriter:
    file = ""
    start_time = 0

    def __init__(self, file, header, starttime):
        """
        Inits file with header and saves starttime for logging with write_stats.

        write_stats and write_stat are not meant to be used in the same writer.
        When using write_stat, header and starttime can be omitted or set to "" and 0.

        APPENDS '\n' TO HEADER!
        """
        self.start_time = starttime
        self.file = file

        backup = f"{file}.back"
        # Check if the file exists and is a file
        if os.path.isfile(file):
            print(f"Stats file exists, moving to file {backup}")
            os.rename(file, backup)

        with open(file, "w", encoding="utf-8") as f:
            # Write anything to file only if the header is set.
            # Empty header indicates usage of write_stat
            if header != "":
                f.write(f"time,{header}\n")

    def write_stats(self, data):
        """Writes data to the initialized file. APPENDS '\n' TO DATA!"""
        elapsed = self.get_time(time.time_ns() - self.start_time)
        # elapsed_seconds = elapsed / 1000 / 1000 / 1000
        # elapsed_seconds = round(elapsed_seconds, 2)
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(f"{elapsed},{data}\n")

    def write_stat(self, data):
        """
        Write data to stats file. No extra timestamps or headers.
        NOT MEANT TO MIX WITH write_stats.
        """
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(f"{str(data)}\n")

    # Takes one param 'time' as unix time stamp (nanoseconds) and prints only
    # that time into file but with little rounded and changed to milliseconds
    def write_time(self, time):
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(f"{str(self.get_time(time))}\n")

    # This simple helper function is used to have similar time representation
    # everywhere
    def get_time(self, data):
        return round(data / 1000 / 1000, 2)
