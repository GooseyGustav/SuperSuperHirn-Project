from .code import Code
from .feedback import Feedback


class Attempt:
    def __init__(self, code: Code, feedback: Feedback):
        self._code: Code = code
        self._feedback: Feedback = feedback

    def getAttempt(self) -> tuple[Code, Feedback]:
        return (self._code, self._feedback)

    def __repr__(self):
        return f"Attempt(code={self._code}, feedback={self._feedback})"
