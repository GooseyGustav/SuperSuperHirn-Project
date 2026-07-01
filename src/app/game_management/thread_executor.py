import logging
import threading


class ThreadExecutor:
    def run(self, fn):
        def guarded():
            try:
                fn()
            except Exception:
                logging.error("Game thread crashed", exc_info=True)

        threading.Thread(target=fn, daemon=True).start()
