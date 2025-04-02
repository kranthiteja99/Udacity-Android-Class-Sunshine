# Livekit Battle Test - Project Documentation

## 📌 Project Overview
This project is a benchmarking tool designed to evaluate AI voice agents by simulating conversations with various customer personas. The goal is to test whether an AI agent can:
1. Accurately extract the customer's **name** and **ZIP code** from noisy, natural conversations.
2. Convince the customer to speak to a human sales agent.
3. Complete the interaction successfully by reaching the `transfer_call()` stage.

The tool is designed to be extensible, auditable, and easy to run via CLI.

---

## 📝 Instructions & Restrictions

- This project was used as part of a take-home assignment for Stoke.
- Expected duration: **4–6 hours** (flexible as needed).
- AI tools like ChatGPT may be used, but you must complete the work yourself.
- Document any AI tools or setup deviations in `docs.md`.
- Stoke may reimburse up to **$50** in project-related expenses.

---

## ⚙️ Dev Setup

### Required Tools
Install these globally (must be in your `$PATH`):
- [`just`](https://just.systems/man/en/packages.html) – script runner
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) – Python package manager
- [`ruff`](https://docs.astral.sh/ruff/installation/) – linter & formatter

### Common Commands
- `just` or `just help` – Show available commands
- `just build` – Sync dependencies using `uv`
- `just test` – Run tests with `pytest`
- `just run` – Run the CLI entrypoint

---

## 📂 Project Structure

```
interview-kranthi-main/
├── LICENSE
├── README.md
├── docs.md
├── justfile                  # Project tasks and commands
├── pyproject.toml            # Python project metadata and deps
├── ruff.toml                 # Code style configuration
├── uv.lock                   # Dependency lockfile
│
├── benchmark_report.csv      # Results in CSV format
├── benchmark_report.json     # Results with full metadata and transcripts
├── personas.json             # Customer persona definitions
│
├── rec/                      # 🎧 Audio recordings per persona
│   ├── *.m4a, *.wav          # Audio files
│
├── conversation_logs/        # 📒 Segment-by-segment logs per conversation
│   ├── persona_name.json     # Labeled segments with timestamps
│
└── src/
    └── battle_test/
        ├── __init__.py
        ├── cli.py            # Typer CLI for launching benchmarks, inspecting data
        ├── main.py           # Benchmarking engine: loads audio, transcribes, evaluates
        ├── utils.py          # Extraction logic (name, zip), fuzzy match, segment analysis
    └── tests/
        └── test_sanity.py    # Basic testing scaffold with Pytest
```

### 📄 Breakdown of `src/` Files

#### `battle_test/__init__.py`
- Empty initializer to treat `battle_test` as a Python package.

#### `battle_test/main.py`
- The **core benchmarking logic**.
- Runs the full benchmark loop: load personas, transcribe audio, extract data, evaluate success, and output reports.
- Uses helper functions from `utils.py`.

#### `battle_test/utils.py`
- Contains **helper logic** for:
  - Extracting name and ZIP from transcripts.
  - Fuzzy name comparison.
  - Agreement and transfer detection.
- Keeps logic modular and testable.

#### `battle_test/cli.py`
- Defines the **command-line interface** using Typer.
- Includes commands:
  - `benchmark`: run the full test suite.
  - `show-personas`: print all persona definitions.

#### `tests/test_sanity.py`
- A minimal **pytest** example to confirm the environment and toolchain are working.
- Can be extended to test logic in `utils.py`.

---

## 🎯 Project Objective

Build a benchmarking tool to evaluate AI voice agents on their ability to collect customer information under various simulated conditions. The tool should:
- Use voice conversations (not text-only bots)
- Handle different user behaviors (noisy, hesitant, curious, etc.)
- Output performance metrics for agent evaluation

---

## 📊 Core Requirements

1. **Persona Definitions**
   - Define personas with traits, expected name/ZIP, and audio files
   - At least 10 unique personas

2. **Benchmark Execution**
   - AI bot must collect name + ZIP
   - Bot must pitch talking to a sales agent
   - Simulate real conversation flows from recordings

3. **Success Criteria**
   - Correct name + ZIP extracted
   - Customer agrees to talk to sales
   - Bot reaches `transfer_call()` step

4. **Performance Reports**
   - Aggregated stats: success rate, failure reasons, persona breakdowns
   - Output to both `.csv` and `.json`
   - Support future enhancements like dashboards or graphs

---

## ⚙️ How It Works

1. **Audio Transcription**
   - Uses OpenAI Whisper to transcribe `.m4a` and `.wav` files in `/rec/`

2. **Speaker Segmentation**
   - Assigns lines to `bot` or `user` using heuristics (e.g., questions vs. affirmations)
   - Splits segments where both bot and user speak in a single utterance

3. **Information Extraction**
   - Extracts name using regex patterns and fuzzy logic
   - Extracts ZIP using digit pattern matching (strict only — no fuzzy ZIP)

4. **Success Logic**
   - Only succeeds if all conditions are met:
     - name_correct ✅
     - zip_correct ✅
     - customer_agreed ✅
     - bot_transferred ✅

5. **Reporting**
   - Outputs `.csv` and `.json`
   - Generates `conversation_logs/` per call with speaker-tagged segments
   - ✅ Adds `failure_reasons` list for each persona entry in `benchmark_report.json`, identifying exactly what caused the failure (e.g., `missing_zip`, `wrong_name`, `bot_no_transfer`, etc.)

---

## 🧑‍💼 How We Implemented It

- The CLI entry point (`cli.py`) uses [Typer](https://typer.tiangolo.com) to expose commands like `benchmark` and `show-personas`.
- The main benchmarking logic is inside `main.py`, which:
  - Loads persona definitions from `personas.json`
  - Runs Whisper on each audio file to get transcriptions
  - Segments bot vs. user utterances
  - Extracts names and ZIPs using custom logic from `utils.py`
  - Evaluates success conditions
  - Saves per-call logs and final reports to `benchmark_report.json` and `.csv`

- All helper functions (name/zip extraction, matching, agreement detection) live in `utils.py` for reusability.
- The benchmark also logs segment-level details per persona for review/debugging.

---

## 🔄 Main Workflow and Function Calls

The workflow begins in `main.py` with the `run_benchmark()` function:

1. **Load Persona Definitions**
   - From `personas.json` → list of persona dicts

2. **Loop Through Each Persona**
   - Load their associated audio file
   - Transcribe audio with Whisper: `model.transcribe()`
   - Segment the transcript into `conversation_segments`
     - Label each segment with `speaker: bot` or `user`

3. **Extract Information**
   - Call `extract_name(transcript)` → from `utils.py`
   - Call `extract_zip(transcript)` → from `utils.py`
   - Call `customer_agreed(segments)` → detects agreement responses
   - Call `bot_attempted_transfer(transcript)` → detects transfer intent

4. **Evaluate Success**
   - Check if name/zip match expected values
   - Check if customer agreed + bot tried transfer
   - Collect detailed `failure_reasons` per audio for later review

5. **Log Results**
   - Store all results in a dictionary
   - Save per-persona logs to `conversation_logs/`
   - Dump full results to `benchmark_report.json` and `.csv`

6. **Summary and Printout**
   - Print success/failure count and reasons
   - Group partial failures for debugging

---

## 🚀 How We Executed It

1. Place audio files in `/rec/` and define personas in `personas.json`.
2. Run the benchmark:
   ```bash
   just run 
   ```
3. After execution, view results in:
   - `benchmark_report.json`
   - `benchmark_report.csv`
   - `conversation_logs/` per call

4. Optionally inspect personas:
   ```bash
   just run show-personas
   ```

This workflow supports both experimentation and easy repeatable evaluation.

---

## 💬 CLI Usage

- `just run`
  > Runs the full benchmarking suite and outputs reports.

- `just run show-personas`
  > Pretty-prints all loaded personas with traits and audio file names.


---

## ✅ Evaluation Metrics

- Total tests run
- Success rate
- Common failure reasons:
  - Name/ZIP missing or incorrect
  - Customer disagreement
  - Bot failed to transfer
- Success/failure by persona and traits (e.g., noisy, hesitant, etc.)

---

## 🧠 Future Improvements

- Improved speaker diarization (or ASR alternatives)
- Relaxed vs. strict benchmarking modes
- Web dashboard for visual insights
- Persona-type analytics (e.g. noisy vs. cooperative)
- Better fallbacks for fuzzy audio

