# CPU Codebreaker Explanation

> The CPU Codebreaker is an **artificial player** for the Mastermind game. It attempts to **discover** the **secret code** by maintaining a set of all possible solutions that remain consistent with previous feedback and **selecting guesses that maximize information gain** using a **variation of Knuth's Minimax algorithm**.


## Knuth's Minimax algorithm.

### Normal Algorithm

### Our Variation


## Structure of Method Explanation


## Method Overview list

| Method | Description |
| --- | --- |
| method1 | description1 |

## Method Explanations

### `get_guess()`

---

#### General:

***Type:*** *Instance Method*

***Visibility:*** *public*

***Method Signature:***

```python
def get_guess(self, attemptList: list[
        tuple[tuple[int], tuple[int]]
    ]) -> list[int]:
```


***Params:***

> `attemptList: list[tuple[tuple[int], tuple[int]]]`
> - The entire list of **attempts that have been made so far**. One single attempt consists of a guess (tuple[int]) and the respective feedback (tuple[int]).
> 

***Returns:***

> list[int]: The guess required by the game engine from the playerRole: Codebreaker.

---

#### Content:


