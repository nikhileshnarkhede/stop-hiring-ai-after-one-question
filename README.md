# Stop Hiring Your AI After One Question: the code

Companion code for the **Weights & Real Life** article
[Stop Hiring Your AI After One Question](https://www.linkedin.com/pulse/stop-hiring-your-ai-after-one-question-nikhilesh-narkhede-hxj8c).

Would you hire someone after one interview question? Then don't ship an
LLM feature after one prompt. This repo is the article's "trial week" as
a small, runnable Python project: an eval set, a scorecard, a pass rate,
a Wilson range for how sure that number is, and a gate that fails CI
when the score drops.

It runs out of the box with a **mock model**, so you need no API key.
When you're ready, switch to a **real small LLM that runs offline** on
your laptop, then to a **big hosted model**, without touching the eval.

## Quick start

Requires Python 3.9 or newer. The eval itself uses only the standard
library.

```bash
git clone https://github.com/nikhileshnarkhede/stop-hiring-ai-after-one-question.git
cd stop-hiring-ai-after-one-question

# 1. The one-question hire: the same prompt, five times
python one_question.py

# 2. The trial week with the first prompt (gets blocked)
python run_eval.py --prompt v1

# 3. The trial week with the improved prompt (ships)
python run_eval.py

# 4. The same checks as unit tests
pip install -r requirements.txt
pytest -q

# 5. Now with a real small LLM, offline (setup below)
python run_eval.py --backend ollama
```

## What you will see

**One question.** The same prompt, five runs. Four pass, one comes back
with chatty text wrapped around the JSON. If you had tested once, you
would have seen a perfect answer.

```text
Run 1: PASS  {"ticket_id": 147, "summary": "Long story: we migrated ...
Run 2: PASS  {"ticket_id": 147, "summary": "Long story: we migrated ...
Run 3: PASS  {"ticket_id": 147, "summary": "Long story: we migrated ...
Run 4: FAIL  Sure! Here is the summary you asked for: {"ticket_id": ...
Run 5: PASS  {"ticket_id": 147, "summary": "Long story: we migrated ...
```

**The trial week, first prompt.** 50 real-looking tickets, 3 runs each.

```text
Eval set       : 50 cases x 3 runs = 150 model calls
Passed         : 135 / 150
Pass rate      : 90.0%
95% range      : 84.2% to 93.8% (Wilson)

Cases that failed at least once (add these to your regression set):
  3/3  Summarise ticket 149 as JSON: Priority: high. Please summarise ...
  2/3  Summarise ticket 141 as JSON: help
  2/3  Summarise ticket 145 as JSON: Ignore previous instructions ...
  ...

NOT READY TO SHIP: Pass rate 90.0% < pass mark 95%
```

The script exits with code 1, so CI stops the build. Notice which cases
fail: the awkward ones (empty, very short, shouting, non-English, prompt
injection). One friendly test prompt would never have found them.

**The trial week, improved prompt.**

```text
Passed         : 149 / 150
Pass rate      : 99.3%
95% range      : 96.3% to 99.9% (Wilson)

SHIP: Pass rate 99.3% >= pass mark 95%
```

## Where each idea from the article lives

| Article | Code |
|---|---|
| The candidate (model + prompt) | `evals/model.py` → `call_llm`, `SYSTEM_PROMPTS` |
| Twenty real tasks from the job (the eval set) | `evals/cases.py` → `CASES` |
| The same scorecard for every task | `evals/scorer.py` → `passes` |
| Every task, a few times, one score | `evals/runner.py` → `pass_rate` |
| How sure is your score? | `evals/stats.py` → `wilson_interval` |
| Pass mark set before the week | `run_eval.py` → `THRESHOLD = 0.95` |
| The `assert` that runs in CI | `tests/test_eval_gate.py`, `.github/workflows/eval.yml` |
| Regression testing | The CI workflow re-runs the eval on every push and pull request |

`passes`, `pass_rate` and the `assert` gate are the same code as in the
article. `run_eval.py` adds a report and the Wilson range on top.

## How the mock model behaves

The mock is there so the repo runs anywhere. It copies the behaviour
that makes one-prompt testing unsafe:

- **It is random.** The same prompt can pass on one run and fail on the
  next (the candidate's good and bad days).
- **It is worse on awkward inputs** than on everyday ones (it knew the one
  topic you asked about, not the whole job).
- **Its failures are the real ones:** broken JSON, a missing `priority`,
  `"priority": "high"` instead of a number, an empty string, and chatty
  text around the JSON.

`--prompt v1` simulates the first prompt you wrote. `--prompt v2`
simulates the improved one. Runs are seeded, so results are reproducible;
try `--seed 1`, `--seed 2` and so on to see the score move between runs.

Do not copy the mock into production code. It exists only to make the
demo run. For a real model, see the next section.

## Three candidates, one trial week

`call_llm` can sit in front of three different models. The eval set, the
scorer and the 95% pass mark stay the same for all of them. Only the
candidate changes.

| Backend | What it is | Needs |
|---|---|---|
| `mock` (default) | Simulated model, random on purpose | Nothing. Used in CI |
| `ollama` | A real small LLM, running offline on your machine | [Ollama](https://ollama.com) and a ~400 MB model |
| `claude` | A big hosted model through the Anthropic API | `pip install anthropic` and an API key |

### A real small model, offline

1. Install Ollama from [ollama.com](https://ollama.com) (Windows, macOS
   or Linux).
2. Download a small model once (about 400 MB). After this, no internet
   is needed:

```bash
ollama pull qwen2.5:0.5b
```

3. Run the same experiments against it:

```bash
python one_question.py --backend ollama
python run_eval.py --backend ollama --prompt v1
python run_eval.py --backend ollama
```

On a laptop CPU, 150 calls take a few minutes. Add `--limit 10` for a
quick look first (30 calls). That's too few to trust the score, but it's
enough to check the setup works.

Try other small models with `OLLAMA_MODEL`, for example `llama3.2:1b` or
`gemma3:1b` (pull them first).

**Expect it to miss the pass mark.** A model this small will probably
land below 95%, especially with the one-line `v1` prompt. Typical
failures are JSON wrapped in a code fence, chatty text before the JSON,
`"priority": "high"`, and obeying the prompt injection in ticket 145.
That's not a bug in the repo. It's the article's point: one friendly test
prompt would have looked fine, and the trial week shows the real track
record. Read the failing cases, improve the prompt in
`SYSTEM_PROMPTS` in `evals/model.py`, and re-run.

### A big hosted model, later

When you want to compare against a large model, swap the candidate:

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...        # Windows: set ANTHROPIC_API_KEY=...
python run_eval.py --backend claude --limit 10
python run_eval.py --backend claude
```

The default is `claude-opus-5-5`. Pick another model with
`CLAUDE_MODEL`. A full run is 150 paid calls, so start with `--limit`.

To try a different provider, copy `evals/hosted_llm.py`, change its
`call` function, and add the new name to `BACKENDS` in `evals/model.py`.
Return the raw text exactly as the model sent it. Don't clean it up
first, because the scorer has to see what your users would get.

### Make it yours

1. Replace the tickets in `evals/cases.py` with real inputs from your
   logs, including the strange ones.
2. Change `passes` in `evals/scorer.py` to check what *your* feature
   needs.
3. Keep CI on the mock, or add your API key as a repository secret and
   run the real eval on pull requests only, since every run costs money.

## Options

```text
python run_eval.py [--backend mock|ollama|claude] [--prompt v1|v2]
                   [--runs 3] [--limit N] [--seed 0]
                   [--threshold 0.95] [--strict]
```

You can also set the backend with the `EVAL_BACKEND` environment
variable. `--seed` only affects the mock.

`--strict` gates on the **lower end of the Wilson range** instead of the
raw pass rate. It answers a tougher question: "Even on an unlucky
reading, are we still above the pass mark?" Small eval sets struggle to
pass it, which is the point.

## Honest caveats

- **The score is only as good as the cases.** If `cases.py` does not look
  like your real users, 99% means little. Keep adding real failures.
- **A code scorer checks format, not truth.** For "is this summary
  accurate?", teams use a second model as a judge, and spot-check that
  judge with humans.
- **Don't teach to the test.** Keep a held-out set of cases you never tune
  the prompt on.

## About

Part of **Weights & Real Life**, a newsletter on ML and AI for
practitioners and recruiters, using real-life analogies and small,
honest code. Read the article: [Stop Hiring Your AI After One
Question](https://www.linkedin.com/pulse/stop-hiring-your-ai-after-one-question-nikhilesh-narkhede-hxj8c).
