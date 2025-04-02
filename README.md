# Livekit Battle Test

This repository is a sample project used for interviewing with Stoke.

1. Start by reading the Instructions & Restrictions section.
2. Then work through the "Dev Setup" and make sure you can run the `just test`
   and `just run` commands succesfully.
3. Finally, start implementing the workflow engine as described in the
   "Project Spec" section.

# Instructions & Restrictions

This is a take home coding assignment. We expect you to spend roughly
**4-6 hours** working on this project. If you find yourself spending more or
less time on the project please adjust the deliverables accordingly and make
note of the changes. It's possible our time and scope estimates are far off.

(This is not a hard time limit, we just do not want to ask for more than this
amount of your time during this portion of the interview. But feel free to spend
more or less time as needed.)

During the assignment you may use any tools you wish, as long as you are the one
building the project. For example, you may use any AI coding assistants, but you
may NOT have your friend build the project for you. If you are using AI tools,
please write down the tool names briefly in `docs.md`.  Stoke will reimburse you up
to $50 for costs incurred in the execution of this project. 

# Dev Setup

_Note: This is the recommended setup, but you are free to change any settings as
needed. **Please document any dev setup changes in `docs.md` so we can run your
code.** (Our only ask here is to keep using `uv` if possible, but you may even
change that with good reason.)_

## Install

Install the following tools (globally, so they are in your `$PATH`):

- [`just`](https://just.systems/man/en/packages.html) (script runner)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (python package manager)
- [`ruff`](https://docs.astral.sh/ruff/installation/) (python linter & formatter)

## Common Commands

- `just` or `just help`
  - Prints the available repo commands.
- `just build`
  - Syncs depedencies and builds everything with `uv`.
  - See `pyrpoject.toml` to add more dependencies.
- `just test`
  - Runs tests with `uv` and `pytest`.
  - See `src/tests/test_sanity.py` for an example.
  - See `pyproject.toml` section `[tool.pytest]` for settings.
- `just run`
  - Runs the main with `uv run`.
  - See `src/battle_test/main.py` for implementation.
  - See `pyproject.toml` section `[project.scripts]` for settings or to add more
    `uv run` targets.

# Project Spec

### **Context**
Our company is continuously improving AI-driven voice agents to enhance customer interactions 
and streamline business processes. Evaluating the impact of changes in voice models, scripts, and 
configurations currently requires live deployment, making iteration slow and difficult to measure. 
A structured benchmarking framework would allow us to simulate diverse customer interactions,
ensuring our bots perform optimally before deployment, reducing risk, improving efficiency, and
driving better outcomes in customer engagement and conversion rates.

### **Objective**

Build a benchmarking tool to evaluate AI voice agents on their ability to collect customer information
under various simulated conditions. The tool will allow the execution of structured tests against 
predefined customer personas and generate performance metrics.

### **Core Requirements**

1. **Customer Persona Definitions**
   - Users should be able to define a suite of customer personas with different characteristics (e.g.,
     clear speech, heavy accents, background noise, hesitant responses, interruptions).
   - Each persona should have predefined behaviors affecting their response pattern.
   - There should be a minimum of 10 test personas. 
2. **Benchmarking Test Execution**
   - The AI voice agent's job is to collect a customer's name and zip code and convince the consumer to
     agree to speak to a sales agent about purchasing a new sprocket.  It isn't a sprocket salesperson
     itself, but should be reasonably capable in trying to pitch the value of speaking to a sales agent.
   - The benchmarking tool should evaluate success metrics for the voice agent against the suite of test personas.
   - The benchmarking should be of voice conversations, not LLMs interacting directly via text. 
3. **Success/Failure Tracking**
   - A call is considered successful if:
     - The bot correctly captures both the **name** and **zip code**.
     - The customer agrees to speak to a sales agent. 
     - The bot reaches the `transfer_call()` step.
   - A call is considered failed if:
     - Either piece of information is missing or incorrect.
     - The conversation terminates before reaching `transfer_call()`.
4. **Performance Aggregation**
   - Generate aggregate performance metrics showing the success rate across all personas.
   - Provide a breakdown by persona to identify failure patterns in specific customer types.
   - An ideal solution provides insight into main points of failure to improve iteration speed.

### **Implementation Guidelines**

#### **Test Execution**

- The tool should iterate through all personas and simulate interactions.
- The bot's responses should be logged along with timestamps.

#### **Output Metrics**

- Generate a report in JSON or CSV format summarizing:
  - Total tests run
  - Success rate (%)
  - Breakdown of success vs. failure by persona
  - Common failure points

### **Deliverables**

- A runnable Python script (or preferred language) implementing the benchmarking tool.
- A test with at least 5 personas - easily extensible
- Sample test run with generated output metrics.
- (Optional) Any additional enhancements that demonstrate problem-solving and creativity.

### **Evaluation Criteria**

- Code quality and structure
- Ability to define and execute structured tests
- Clarity and effectiveness of test results
- Creativity in handling customer personas and failure scenarios



# License

[MIT](./LICENSE)
