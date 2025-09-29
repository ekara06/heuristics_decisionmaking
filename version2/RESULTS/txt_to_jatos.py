import os
import glob
import json
from collections import Counter

#THIS SCRIPT CONVERT TXT TO JSON AND COUNT THE TARGETS, CHOICE BUTTONS, OPTION SELECTIONS, AND ATTENTION CHECKS


def main(input_pattern="/Users/elifkara/Desktop/Helmholtz/RESULTS/ranking_data/**/*.txt", output_folder="json_output"):
    os.makedirs(output_folder, exist_ok=True)

    condition_counts = Counter()
    attention_distribution = Counter()  # 0–4 passed per file
    choice_button_counts = Counter()
    selected_option_counts = Counter()
    target_counts = Counter()

    txt_files = glob.glob(input_pattern, recursive=True)
    print(f"Found {len(txt_files)} files")

    converted_count = 0
    script_root = os.path.abspath(os.path.dirname(__file__))

    for txt_path in txt_files:
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            condition_group = data.get("condition_group", "unknown")
            condition_counts[condition_group] += 1
            responses = data.get("responses", [])

            # ---- Attention check counting ----
            attn_checks = [r for r in responses 
                           if isinstance(r, dict) and isinstance(r.get("question"), str) 
                           and "attention_check" in r["question"]]
            passed_count = sum(1 for r in attn_checks if r.get("passed", False))
            attention_distribution[passed_count] += 1

            # ---- Regular question counting ----
            for r in responses:
                if isinstance(r, dict) and "target" in r:
                    target_counts[r["target"]] += 1

                    choice = r.get("choice", {})
                    if isinstance(choice, dict):
                        button = choice.get("button")
                        selected_option = choice.get("selected_option")

                        if button:
                            choice_button_counts[button] += 1
                        if selected_option:
                            selected_option_counts[selected_option] += 1

            # ---- Write per-file JSON next to summary output (preserve subfolders) ----
            rel_path_from_root = os.path.relpath(os.path.abspath(txt_path), script_root)
            json_rel_path = rel_path_from_root[:-4] + '.json' if rel_path_from_root.lower().endswith('.txt') else rel_path_from_root + '.json'
            json_out_path = os.path.join(output_folder, json_rel_path)
            os.makedirs(os.path.dirname(json_out_path), exist_ok=True)
            with open(json_out_path, 'w', encoding='utf-8') as jf:
                json.dump(data, jf, ensure_ascii=False, indent=2)
            converted_count += 1

        except Exception as e:
            print(f"Error processing {txt_path}: {e}")
            continue

    # ---- Print summary ----
    print("\nCONDITION GROUPS:")
    for condition, count in condition_counts.most_common():
        print(f"  {condition}: {count} files")

    print("\nATTENTION CHECK SUMMARY:")
    for k in sorted(attention_distribution.keys()):
        print(f"  Files with {k} attention checks passed: {attention_distribution[k]}")
    print(f"  Files that failed ALL 4 checks: {attention_distribution.get(0, 0)}")

    print("\nCHOICE BUTTON DISTRIBUTION:")
    for button, count in choice_button_counts.most_common():
        print(f"  {button}: {count} choices")

    print("\nOPTION SELECTION DISTRIBUTION:")
    for option, count in selected_option_counts.most_common():
        print(f"  {option}: {count} selections")

    print("\nALL TARGETS AND THEIR FREQUENCIES:")
    for target, count in sorted(target_counts.items()):
        print(f"  '{target}': {count} times")

    # ---- Save summary ----
    os.makedirs(output_folder, exist_ok=True)
    summary = {
        "condition_groups": dict(condition_counts),
        "attention_check_summary": dict(attention_distribution),
        "choice_buttons": dict(choice_button_counts),
        "selected_options": dict(selected_option_counts),
        "target_counts": dict(target_counts)
    }
    out_path = os.path.join(output_folder, "summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved summary to {out_path}")
    print(f"Converted {converted_count} files to JSON under '{output_folder}'")

if __name__ == "__main__":
    main()
