# CPU Codebreaker Explanation

> The CPU Codebreaker is an **artificial player** for the Mastermind game. It attempts to **discover** the **secret code** by maintaining a set of all possible solutions that remain consistent with previous feedback and **selecting guesses that maximize information gain** using a **variation of Knuth's Minimax algorithm**.

## Knuth's Minimax algorithm.

### <u>Normal Algorithm</u>

> Knuth's Minimax works efficiently algorithm (1977) solves Mastermind optimally by guaranteeing a solution within five guesses for a standard 4-peg, 6-color game. The core idea is to select each guess such that, in the worst case, the remaining candidate space is minimized as much as possible.

[This Stackoverflow Post](https://stackoverflow.com/questions/62430071/donald-knuth-algorithm-mastermind) explains the rundown of the algorithm using the standart Mastermind rules (4 pegs, 6 colors). We've used their approach to convert the logic to our specific game requirements.

> The key property of Minimax is its pessimism: it does not optimize for the average case or the best case, but for the worst case — ensuring a bounded number of guesses regardless of the secret.

### <u>Our Variation</u>

> Our implementation adapts the standard algorithm to a 5-peg, 8-color Mastermind variant, and introduces two practical optimizations to manage the significantly larger codespace (8⁵ = 32,768 codes instead of 6⁴ = 1,296).

Keep in mind, that all of the **32,768** codes must be checked **against all possible secret codes**. For the first guess (without being fixed value), this would be _32.768_ (possible codes for guess) × _32.768_ (possible secret codes) ≈ **1,07 Billion comparisons**.

**Optimization 1 — Candidate-only guess pool**:
Rather than evaluating every code in the full codespace as a potential next guess, only the remaining candidates are considered.

**Optimization 2 — Deterministic sampling for large candidate sets**:
When the candidate set is large (above `_MINIMAX_SAMPLE_THRESHOLD = 200`), evaluating every candidate against every other candidate would cause an O(n²) lookup. Instead, a uniform deterministic sample is taken via slicing (`candidates[::step]`). Using slicing rather than random sampling ensures that `get_guess()` is fully deterministic for the same input history.

Both optimizations trade a small degree of Knuth-optimality for a large gain in runtime, without meaningfully impacting game performance in practice.

## Algorithm Workflow

The codebreaker algorithm contains two steps to figure out the optimal guess.
A thorough description of each method can be found [in this documentation](#method-explanations) further down below.

### 1. Part: Decrease Hypothesis Room

Most of the methods inside the codebreaker class are solely used for this purpose, to optimize the algorithm by narrowing down the list of potential candidates. Otherwise the second step (Minimax) would need to iterate over the entire list of possible guesses (**8⁵ = 32,768 potential guesses**).

### 2. Part: Minimax (Knuth)

After the candidate filtering step, the algorithm has reduced the hypothesis space to only those codes that remain consistent with all previous feedback. The purpose of the Minimax step is to choose the next guess that will eliminate as many of those remaining possibilities as possible, regardless of what feedback is received.

For each potential guess in the guess pool, the algorithm simulates **how that guess would score against every remaining candidate secret**.

Assume the current candidate space contains:

```python
[
    (1, 1, 2, 2, 3),
    (1, 2, 3, 4, 5),
    (5, 4, 3, 2, 1),
    (8, 8, 7, 7, 6)
]
```

Now consider the guess:

```python
(1, 2, 3, 4, 5)
```

The algorithm evaluates **this guess against every candidate** and computes the resulting **feedback pattern**:

```python
{
    (1, 1, 2, 2, 3): (1, 2),
    (1, 2, 3, 4, 5): (5, 0),
    (5, 4, 3, 2, 1): (1, 4),
    (8, 8, 7, 7, 6): (0, 0)
}
```

Candidates producing the same feedback are grouped into a **_partition_**.

For example:

```python
{
    (0, 0): 12 candidates,
    (1, 2): 7 candidates,
    (2, 1): 5 candidates,
    (5, 0): 1 candidate
}
```

The **size** of the **largest partition** determines the worst-case outcome for this guess.

In the example above:

```python
worst_case = 12
```

This means that no matter which feedback is received, at most 12 candidates would remain after the next filtering step.

The algorithm repeats this process for every candidate in the guess pool.

For each guess:

```python
worst_case = max(partitions.values())
```

is calculated.

The guess with the smallest worst-case partition is selected:

```python
best_guess = argmin(worst_case)
```

because it guarantees the largest reduction of the hypothesis space in the least favorable scenario.

## Type Aliases

```python
type Code = tuple[int, int, int, int, int]
type Feedback = tuple[int, ...]
type Attempt = tuple[Code, Feedback, str]
```

Where:

- `Code` represents a valid Mastermind code.
- `Feedback` represents the feedback pegs returned by the game engine.
- `Attempt` represents one completed round consisting of:
  `(guess, feedback, status)`.

## Method Overview list

| Method                                      | Visibility      | Description                                                            |
| ------------------------------------------- | --------------- | ---------------------------------------------------------------------- |
| `get_guess()`                               | public          | Entry point — returns the next guess based on the full attempt history |
| `is_attemptList_valid()`                    | public, static  | Validates the structure and contents of an attempt history             |
| `_calc_candidates()`                        | private         | Applies all previous attempts to reduce the candidate space            |
| `_filter_by_exact_feedback()`               | private         | Filters candidates using exact black/white peg counts                  |
| `_filter_by_provisional_feedback()`         | private         | Filters candidates using only the total match count                    |
| `_feedback_to_counts()`                     | private, static | Converts a feedback tuple into `(black_count, white_count)`            |
| `_calc_candidate_guess_final_match()`       | private, static | Computes exact `(black, white)` feedback for a candidate and guess     |
| `_calc_candidate_guess_provisional_match()` | private, static | Computes the total number of matching colors, ignoring position        |
| `_select_minimax_guess()`                   | private         | Selects the next guess using the Minimax criterion                     |

## Method Explanations

### `get_guess()`

---

**_Type:_** _Instance Method_

**_Visibility:_** _public_

**_Method Signature:_**

```python
def get_guess(
    self,
    attempt_list: list[Attempt]
) -> list[int]:
```

**_Params:_**

> `attempt_list: list[Attempt]`
>
> - The complete history of all previous guesses.
> - Each attempt consists of:
>
>   ```python
>   (guess, feedback, status)
>   ```
>
> - `status` is either `"final"` or `"provisional"`.

**_Returns:_**

> `list[int]`: The guess required by the game engine from the playerRole: Codebreaker.

---

`get_guess()` is the public entry point of the algorithm. It is called once per round by the game engine, and must return the codebreaker's next guess as a list of integers representing color IDs.

On the first call (empty `attemptList`), it immediately returns `_OPENING_GUESS = [1, 1, 2, 2, 3]` — a fixed starting guess chosen to cover three distinct colors and mirror the common convention of starting with repeated values in Knuth-style implementations.

On subsequent calls, it:

1. Delegates to `_calc_candidates()` to determine which codes remain
   consistent with all previous feedback.
2. If exactly one candidate remains, that candidate must be the secret
   code and is returned immediately.
3. Otherwise, delegates to `_select_minimax_guess()` to choose the next
   information-maximizing guess.

---

### `_calc_candidates()`

---

**_Type:_** _Instance Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
def _calc_candidates(
    self,
    attempt_list: list[Attempt]
) -> list[Code]:
```

**_Params:_**

> `attemptList: list[Attempt]`
>
> - The full attempt history, identical in structure to the parameter of `get_guess()`.

**_Returns:_**

> `list[Code]` — The subset of codes from the full codespace that are consistent with every past guess-feedback pair.

---

This method iteratively reduces the current candidate space by applying
every previous attempt as a constraint.

For each attempt the filtering strategy depends on the feedback status:

`"final"`:
`_filter_by_exact_feedback()` is used.
`"provisional"`:
`_filter_by_provisional_feedback()` is used.

Only codes that remain consistent with every previous attempt survive.

If all candidates are eliminated, the feedback history is internally
inconsistent and no unique secret can be derived. In this situation, a
random code from the complete codespace is returned as a fallback.

---

### `_filter_by_exact_feedback()`

**_Type:_** _Instance Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
def _filter_by_exact_feedback(
    self,
    candidates: list[Code],
    guess: Code,
    feedback: Feedback
) -> list[Code]:
```

**_Params:_**

> `candidates: list[Code]`
>
> - The codespace of all possible candidates for the secret code.
>
> `guess: Code`
>
> - The current Guess used for filtering of an Attempt
>
> `feedback: Feedback`
>
> - The respective Feedback used for filtering of the same Attempt

**_Returns:_**

> `list[Code]` — The subset of codes from the full codespace that are consistent with every past guess-feedback pair.

---

Used when the feedback status is `"final"`.

The exact number of black and white pegs is known and therefore every
candidate can be evaluated precisely.

For each candidate:

```python
_calc_candidate_guess_final_match(candidate, guess)
```

is computed.

Only candidates producing exactly the same
`(black_count, white_count)` pair as the received feedback are kept.

---

### `_filter_by_provisional_feedback()`

**_Type:_** _Instance Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
def _filter_by_provisional_feedback(
    self,
    candidates: list[Code],
    guess: Code,
    feedback: Feedback
) -> list[Code]:
```

**_Params:_**

> `candidates: list[Code]`
>
> - The codespace of all possible candidates for the secret code.
>
> `guess: Code`
>
> - The current Guess used for filtering of an Attempt
>
> `feedback: Feedback`
>
> - The respective Feedback used for filtering of the same Attempt

**_Returns:_**

> `list[Code]` — The subset of codes from the full codespace that are consistent with every past guess-feedback pair including provisional feedbacks.

---

Used when the feedback status is `"provisional"`.

Some Pegs in the feedback are returned as white pegs altough some may actually
respresent black pegs.

The only reliable information is the amount of pegs in the feedback

A candidate is kept if its total color-match count equals the number of
feedback pegs received.

---

**_Type:_** _Static Method_

**_Visibility:_** \_public\_\_

**_Method Signature:_**

```python
@staticmethod
def is_attemptList_valid(
    attempt_list: list[Attempt]
) -> bool:
```

**_Params:_**

> `attempt_list: list[Attempt]`
>
> - The complete attempt history supplied to get_guess() with structure: (guess, feedback, status)

**_Returns:_**

> `bool`
>
> - True if every attempt conforms to the expected structure and value ranges.
> - False otherwise.

---

This method validates that each Attempt in the attempt list (guess, feedback, status) are valid.
The different validation checks can be found inside the method.

---

### `_feedback_to_counts()`

---

**_Type:_** _Static Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
@staticmethod
def _feedback_to_counts(
    feedback: Feedback
) -> tuple[int, int]:
```

**_Params:_**

> `feedback: Feedback`
>
> - The feedback of any guess (encoded as integer) containing either `BLACK_PEG = 8` and `WHITE_PEG = 7`.

**_Returns:_**

> `tuple[int, int]` — A `(black_count, white_count)` pair.

---

A parsing utility. It counts the occurrences of `BLACK_PEG` and `WHITE_PEG` in the feedback tuple and returns them as a structured pair.

---

### `_calc_candidate_guess_final_match()`

**_Type:_** _Class Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
@staticmethod
def _calc_candidate_guess_final_match(
    secret: Code,
    guess: Code
) -> tuple[int, int]:
```

**_Params:_**

> `secret: Code`
>
> - The potential secret from the list of candidates

> `guess: Code`
>
> - The guess of the attempt List to check against the potential secret

**_Returns:_**

> `tuple[int, int]` — The amount of black and white pegs that the comparison between `secret` and `guess` has.

---

Computes the exact Mastermind score for a candidate secret code and a
guess.

Black pegs represent colors that match in both color and position.

White pegs represent colors that exist in the secret code but occupy a
different position.

To prevent double counting, all black-peg matches are removed before
white pegs are calculated.

---

### `_calc_candidate_guess_provisional_match()`

**_Type:_** _Class Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
@staticmethod
def _calc_candidate_guess_provisional_match(
    secret: Code,
    guess: Code
) -> int:
```

**_Params:_**

> `secret: Code`
>
> - The potential secret from the list of candidates

> `guess: Code`
>
> - The guess of the attempt List to check against the potential secret

**_Returns:_**

> `int` — The amount of white pegs (matches) that the comparison between `secret` and `guess` has.

---

Computes the total number of matching colors between a candidate secret
and a guess while completely ignoring position.

Unlike `_calc_candidate_guess_final_match()`, this method does not
distinguish between black and white pegs.

It is exclusively used when evaluating provisional feedback.

---

### `_select_minimax_guess()`

---

#### General

**_Type:_** _Instance Method_

**_Visibility:_** _private_

**_Method Signature:_**

```python
def _select_minimax_guess(
    self,
    candidates: list[tuple[int]]
) -> tuple[int]:
```

**_Params:_**

> `candidates: list[tuple[int]]`
>
> - The current set of viable candidate codes, as returned by `_consistent_candidates()`.

**_Returns:_**

> `tuple[int]` — The guess selected by the Minimax criterion.

---

This method implements the **Minimax selection step**. For each code in the guess pool, it simulates the feedback that code would produce against every remaining candidate, grouping candidates by their resulting feedback pattern into partitions. The **worst-case partition size** for that guess is the maximum over all partition sizes.

The guess with the **smallest worst-case partition** is selected — this is the code that, no matter what feedback the game engine returns, leaves the fewest candidates remaining in the worst case.

**Sampling:** when the candidate set exceeds `_MINIMAX_SAMPLE_THRESHOLD = 200`, a uniform step is computed as `step = max(1, len(candidates) // threshold)` and the guess pool is reduced to `candidates[::step]`. This deterministic slice ensures that the method remains **side-effect free and reproducible**, unlike random sampling.
