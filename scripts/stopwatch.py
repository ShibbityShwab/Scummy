import time

class Stopwatch:
    def start(self):
        self.startTime = time.perf_counter()
    def stop(self):
        self.stopTime = time.perf_counter()
    def elapsedTime(self):
        return f"Completed in {self.stopTime - self.startTime} seconds."