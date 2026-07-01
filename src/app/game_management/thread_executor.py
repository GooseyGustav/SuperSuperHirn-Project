import threading


class ThreadExecutor:
    def run(self, fn):
        threading.Thread(target=fn, daemon=True).start()
