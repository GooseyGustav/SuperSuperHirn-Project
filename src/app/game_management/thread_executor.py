import threading


class ThreadExecutor:
    def run(self, fn):
        print("run thread")
        threading.Thread(target=fn, daemon=True).start()
