#!/usr/bin/env python3
"""
Formula Meaning Calibration Tester
Tests LLM memory/understanding capabilities by comparing its formula
word-interpretations against the canonical pattern table.

Usage:
    python3 formula_test.py [--seed 42] [--sample 10] [--export results.json]
"""

import json
import random
import sys
import argparse
import textwrap
from pathlib import Path

TABLE_PATH = Path(__file__).parent / "formula_table.json"


def load_table(path: Path) -> list:
    with open(path, "r") as f:
        return json.load(f)


def extract_words(text: str) -> set:
    """Extract lowercase alphabetic tokens from a string."""
    return {w.lower() for w in text.replace("/", " ").replace("-", " ").split()}


def score_interpretation(predicted: str, target: str) -> dict:
    """
    Compare predicted word-interpretation against the target.
    Returns token overlap metrics.
    """
    pred_tokens = extract_words(predicted)
    targ_tokens = extract_words(target)

    intersection = pred_tokens & targ_tokens
    union = pred_tokens | targ_tokens

    precision = len(intersection) / len(pred_tokens) if pred_tokens else 0.0
    recall = len(intersection) / len(targ_tokens) if targ_tokens else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "predicted": predicted,
        "target": target,
        "pred_tokens": sorted(pred_tokens),
        "targ_tokens": sorted(targ_tokens),
        "match_tokens": sorted(intersection),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def evaluate(entry: dict, model_output: str) -> dict:
    result = score_interpretation(model_output, entry["word_interpretation"])
    result["id"] = entry["id"]
    result["formula"] = entry["formula"]
    result["category"] = entry["category"]
    return result


def build_prompt(entry: dict) -> str:
    return textwrap.dedent(f"""
        Formula interpretation task.

        The formula is: {entry['formula']}
        Canonical reading: {entry['canonical']}

        Give ONLY a short phonetic word-interpretation for this formula,
        following the style: e im code two, f gravity mass me one me two dont do
        (one interpretation per symbol/phoneme, lowercase, space-separated).
        Output only the interpretation, nothing else.
    """).strip()


def run_test(table: list, seed: int = 42, sample_size: int = None) -> dict:
    """
    Run calibration test.  Since this module does not embed an LLM,
    it returns the test *cases* formatted for external LLM evaluation,
    plus a rubric describing how to score results.
    """
    rng = random.Random(seed)
    pool = table.copy()
    rng.shuffle(pool)

    if sample_size:
        pool = pool[:sample_size]

    cases = []
    for entry in pool:
        cases.append({
            "id": entry["id"],
            "formula": entry["formula"],
            "canonical": entry["canonical"],
            "target_interpretation": entry["word_interpretation"],
            "token_map": entry["token_map"],
            "prompt": build_prompt(entry),
        })

    rubric = {
        "description": (
            "For each case, submit the prompt to an LLM and collect its "
            "word-interpretation.  Score with score_interpretation()."
        ),
        "metrics": ["precision", "recall", "f1"],
        "pass_threshold": {
            "f1_90": 0.90,
            "f1_75": 0.75,
            "f1_50": 0.50,
        },
        "aggregation": (
            "mean_f1 across all cases, plus per-category breakdown."
        ),
    }

    return {
        "seed": seed,
        "total_cases": len(cases),
        "rubric": rubric,
        "cases": cases,
    }


def print_summary(results: list):
    if not results:
        print("No results to summarize.")
        return

    avg_f1 = sum(r["f1"] for r in results) / len(results)
    avg_prec = sum(r["precision"] for r in results) / len(results)
    avg_rec = sum(r["recall"] for r in results) / len(results)

    print("\n=== Formula Interpretation Test Summary ===")
    print(f"  Cases evaluated : {len(results)}")
    print(f"  Avg Precision   : {avg_prec:.2%}")
    print(f"  Avg Recall      : {avg_rec:.2%}")
    print(f"  Avg F1          : {avg_f1:.2%}")

    thresholds = [(0.90, "EXCELLENT"), (0.75, "GOOD"), (0.50, "MODERATE")]
    for thresh, label in thresholds:
        if avg_f1 >= thresh:
            print(f"  Assessment      : {label} (F1 >= {thresh})")
            break
    else:
        print("  Assessment      : NEEDS CALIBRATION (F1 < 0.50)")

    print("\n  Per-case breakdown:")
    for r in results:
        status = "✓" if r["f1"] >= 0.75 else ("~" if r["f1"] >= 0.50 else "✗")
        print(f"    {status} [{r['id']:3d}] {r['formula']:<25s}  F1={r['f1']:.2%}  "
              f"target=\"{r['target']}\"  pred=\"{r['predicted']}\"")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Test LLM formula interpretation against pattern table"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--sample", type=int, default=None, help="Limit number of cases"
    )
    parser.add_argument(
        "--export", type=str, default=None, help="Export cases to JSON file"
    )
    parser.add_argument(
        "--table", type=str, default=None, help="Path to formula_table.json"
    )
    args = parser.parse_args()

    table_path = Path(args.table) if args.table else TABLE_PATH
    table = load_table(table_path)
    test = run_test(table, seed=args.seed, sample_size=args.sample)

    if args.export:
        with open(args.export, "w") as f:
            json.dump(test, f, indent=2)
        print(f"Exported {test['total_cases']} test cases to {args.export}")

    print(f"\nFormula Interpretation Calibration Test")
    print(f"  Total formulas in table : {len(table)}")
    print(f"  Test cases              : {test['total_cases']}")
    print(f"  Seed                    : {args.seed}")
    print("\nPrompts ready for LLM evaluation.")
    print("To score results, use score_interpretation(predicted, target).")


if __name__ == "__main__":
    main()
