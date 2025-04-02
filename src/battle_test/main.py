import os
import json
import csv
from datetime import datetime
import whisper
from collections import Counter, defaultdict

# Importing helper functions from utils
from battle_test.utils import (
    extract_name, extract_zip, fuzzy_match, customer_agreed, bot_attempted_transfer
)

# File paths and constants
AUDIO_FOLDER = "./rec"
PERSONA_FILE = "./personas.json"
REPORT_FILE_JSON = "./benchmark_report.json"
REPORT_FILE_CSV = "./benchmark_report.csv"
CONVO_LOG_DIR = "./conversation_logs"

# Load Whisper model once at the start
model = whisper.load_model("base")

def classify_segment(text: str, prev_speaker: str = "bot") -> str:
    lower = text.lower()

    user_cues = [
        "my name is", "i'm", "zip is", "yeah", "yes", "sure", "okay", "alright",
        "i guess", "i think", "it's", "that works", "just", "uh", "name's", "not really"
    ]

    bot_cues = [
        "can i", "would you", "shall i", "connecting", "transfer", "let me",
        "please hold", "one moment", "thanks", "perfect", "i understand", "just so you know"
    ]

    if any(cue in lower for cue in user_cues):
        return "user"
    if any(cue in lower for cue in bot_cues):
        return "bot"

    if lower.endswith("?"):
        return "user"

    return prev_speaker

def compute_extra_summary_metrics(results):
    total = len(results)
    if total == 0:
        return {}

    # Component-level performance stats
    name_matches = sum(1 for r in results if r.get("name_correct"))
    zip_matches = sum(1 for r in results if r.get("zip_correct"))
    agreement_matches = sum(1 for r in results if r.get("customer_agreed"))
    transfer_matches = sum(1 for r in results if r.get("bot_transferred"))

    component_accuracy = {
        "name_accuracy": f"{name_matches}/{total}",
        "zip_accuracy": f"{zip_matches}/{total}",
        "customer_agreement_rate": f"{agreement_matches}/{total}",
        "bot_transfer_rate": f"{transfer_matches}/{total}"
    }

    # Count how many calls partially succeeded
    partial_success = Counter()
    for r in results:
        score = sum([
            bool(r.get("name_correct")),
            bool(r.get("zip_correct")),
            bool(r.get("customer_agreed")),
            bool(r.get("bot_transferred"))
        ])
        if score < 4:
            partial_success[f"{score}_of_4"] += 1

    # Track which traits are most associated with failure
    failures_by_trait = defaultdict(int)
    for r in results:
        if not r.get("success"):
            for trait in r.get("traits", []):
                failures_by_trait[trait] += 1

    # Track whether each persona succeeded
    success_by_persona = {
        r["persona"]: r.get("success") for r in results
    }

    return {
        "component_accuracy": component_accuracy,
        "partial_success": dict(partial_success),
        "failures_by_trait": dict(failures_by_trait),
        "success_by_persona": success_by_persona
    }


def run_benchmark():
    # Load all persona test cases
    with open(PERSONA_FILE) as f:
        personas = json.load(f)

    results = []
    failure_reasons = {
        "missing_name": 0,
        "missing_zip": 0,
        "wrong_name": 0,
        "wrong_zip": 0,
        "customer_disagreed": 0,
        "bot_no_transfer": 0
    }

    # Ensure output directory exists
    os.makedirs(CONVO_LOG_DIR, exist_ok=True)

    for persona in personas:
        expected_name = persona["name"].lower().strip()
        expected_zip = persona["zip_code"].strip()
        audio_path = os.path.join(AUDIO_FOLDER, persona["audio_file"])
        traits = persona.get("persona_traits", [])

        # Skip if file not found
        if not os.path.exists(audio_path):
            print(f"❌ Audio file missing: {audio_path}")
            continue

        print(f"\n🔊 Processing: {audio_path}")
        result = model.transcribe(audio_path)  # Transcribe the audio
        transcript = result["text"]
        segments = result.get("segments", [])

        conversation_segments = []
        prev_speaker = "bot"

        for seg in segments:
            text = seg["text"].strip()
            speaker = classify_segment(text, prev_speaker)
            conversation_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": speaker,
            "text": text
            })
            prev_speaker = speaker

        # Extract relevant information
        extracted_name = extract_name(transcript)
        extracted_zip = extract_zip(transcript)
        agreed = customer_agreed(conversation_segments)
        transferred = bot_attempted_transfer(transcript)

        # Compare extracted values with expected ones
        name_correct = extracted_name and fuzzy_match(extracted_name.lower(), expected_name)
        zip_correct = extracted_zip and extracted_zip == expected_zip
        success = name_correct and zip_correct and agreed and transferred

        # Build failure reasons list
        failure_reason_list = []
        if not extracted_name:
            failure_reasons["missing_name"] += 1
            failure_reason_list.append("missing_name")
        elif not name_correct:
            failure_reasons["wrong_name"] += 1
            failure_reason_list.append("wrong_name")

        if not extracted_zip:
            failure_reasons["missing_zip"] += 1
            failure_reason_list.append("missing_zip")
        elif not zip_correct:
            failure_reasons["wrong_zip"] += 1
            failure_reason_list.append("wrong_zip")

        if not agreed:
            failure_reasons["customer_disagreed"] += 1
            failure_reason_list.append("customer_disagreed")

        if not transferred:
            failure_reasons["bot_no_transfer"] += 1
            failure_reason_list.append("bot_no_transfer")

        # Save results for this call
        results.append({
            "persona": expected_name,
            "expected_zip": expected_zip,
            "extracted_name": extracted_name or "Not found",
            "extracted_zip": extracted_zip or "Not found",
            "customer_agreed": agreed,
            "bot_transferred": transferred,
            "name_correct": name_correct,
            "zip_correct": zip_correct,
            "success": success,
            "traits": traits,
            "transcript": transcript,
            "timestamp": datetime.now().isoformat(),
            "conversation_segments": conversation_segments,
            "failure_reasons": failure_reason_list if not success else []
        })

        # Save conversation breakdown to file
        with open(os.path.join(CONVO_LOG_DIR, f"{expected_name.replace(' ', '_')}.json"), "w") as f:
            json.dump(conversation_segments, f, indent=2)

    # Build summary report
    total = len(personas)
    passed = sum(1 for r in results if r["success"])
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "successful": passed,
        "failed": len(results) - passed,
        "success_rate": round(100 * passed / max(len(results), 1), 2),
        "by_persona": results,
        "common_failures": failure_reasons,
        "extra_metrics": compute_extra_summary_metrics(results)
    }

    # Write summary JSON
    with open(REPORT_FILE_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    # Write CSV for spreadsheet/reporting usage
    with open(REPORT_FILE_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "persona", "expected_zip", "extracted_name", "extracted_zip", "customer_agreed",
            "bot_transferred", "name_correct", "zip_correct", "success", "traits", "timestamp"
        ])
        writer.writeheader()
        for row in results:
            writer.writerow({
                **{k: row[k] for k in writer.fieldnames if k in row},
                "traits": ", ".join(row["traits"]),
            })

    # Output summary to console
    print("\n📊 Benchmark Summary")
    print("─" * 30)
    print(f"Total Tests        : {total}")
    print(f"✅ Successful       : {passed}")
    print(f"❌ Failed           : {total - passed}")
    print(f"✔️ Success Rate     : {summary['success_rate']}%")
    print("\n📉 Failure Breakdown")
    for reason, count in failure_reasons.items():
        print(f"{reason.replace('_', ' ').title():<20}: {count}")


def main():
    run_benchmark()
