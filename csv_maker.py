import json
import csv
import os
import glob
from collections import defaultdict

def extract_question_data(response, prolific_id, condition_group, file_name):
    """
    Extract all relevant data from a single question response
    """
    # Skip attention check questions
    if isinstance(response.get('question'), str) and response['question'].startswith('attention_check_'):
        return None
    
    row = {
        'prolific_id': prolific_id,
        'condition_group': condition_group,
        'source_file': file_name,
        'question_number': response.get('question'),
        'target': response.get('target'),
        'target_value': response.get('target_value'),
        'option1': response.get('options', [None, None])[0] if response.get('options') else None,
        'option2': response.get('options', [None, None])[1] if len(response.get('options', [])) > 1 else None,
        'selected_option': response.get('choice', {}).get('selected_option'),
        'button_pressed': response.get('choice', {}).get('button'),
    }
    
    # Extract optionA data
    if 'optionA' in response:
        option_a = response['optionA']
        row.update({
            'optionA_trial_id': option_a.get('trial_id'),
            'optionA_task_id': option_a.get('task_id'),
            'optionA_values': option_a.get('values'),
            'optionA_target_value': option_a.get('target_value')
        })
        
        # Parse values if they're in string format "value1, value2"
        if isinstance(option_a.get('values'), str):
            values = option_a['values'].split(', ')
            row['optionA_value1'] = float(values[0]) if len(values) > 0 and values[0] else None
            row['optionA_value2'] = float(values[1]) if len(values) > 1 and values[1] else None
        else:
            row['optionA_value1'] = None
            row['optionA_value2'] = None
    
    # Extract optionB data
    if 'optionB' in response:
        option_b = response['optionB']
        row.update({
            'optionB_trial_id': option_b.get('trial_id'),
            'optionB_task_id': option_b.get('task_id'),
            'optionB_values': option_b.get('values'),
            'optionB_target_value': option_b.get('target_value')
        })
        
        # Parse values if they're in string format "value1, value2"
        if isinstance(option_b.get('values'), str):
            values = option_b['values'].split(', ')
            row['optionB_value1'] = float(values[0]) if len(values) > 0 and values[0] else None
            row['optionB_value2'] = float(values[1]) if len(values) > 1 and values[1] else None
        else:
            row['optionB_value1'] = None
            row['optionB_value2'] = None
    
    return row

def process_json_files_to_csv(input_directory, output_directory):
    """
    Process filtered JSON files and create separate CSV files for each condition group
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(input_directory, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {input_directory}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Group data by condition_group
    condition_data = defaultdict(list)
    
    # Process each JSON file
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_name = os.path.basename(file_path)
            prolific_id = data.get('prolific_id', 'UNKNOWN')
            condition_group = data.get('condition_group', 'UNKNOWN')
            
            print(f"Processing: {file_name} (condition: {condition_group})")
            
            # Process each question in the responses
            question_count = 0
            for response in data.get('responses', []):
                row_data = extract_question_data(response, prolific_id, condition_group, file_name)
                if row_data:  # Skip None (attention checks)
                    condition_data[condition_group].append(row_data)
                    question_count += 1
            
            print(f"  Extracted {question_count} questions")
            
        except json.JSONDecodeError as e:
            print(f"Error reading {file_name}: Invalid JSON - {e}")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    
    # Define CSV column headers
    headers = [
        'prolific_id', 'condition_group', 'source_file', 'question_number',
        'target', 'target_value', 'option1', 'option2',
        'selected_option', 'button_pressed',
        'optionA_trial_id', 'optionA_task_id', 'optionA_values', 'optionA_target_value',
        'optionA_value1', 'optionA_value2',
        'optionB_trial_id', 'optionB_task_id', 'optionB_values', 'optionB_target_value',
        'optionB_value1', 'optionB_value2'
    ]
    
    # Create CSV files for each condition group
    for condition_group, rows in condition_data.items():
        if not rows:
            print(f"No data found for condition group: {condition_group}")
            continue
            
        csv_filename = f"{condition_group}_data.csv"
        csv_path = os.path.join(output_directory, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n✓ Created {csv_filename} with {len(rows)} rows")
        print(f"  Saved to: {csv_path}")
    
    print(f"\n=== Summary ===")
    print(f"Condition groups found: {list(condition_data.keys())}")
    for condition, rows in condition_data.items():
        unique_files = len(set(row['source_file'] for row in rows))
        print(f"  {condition}: {len(rows)} questions from {unique_files} files")

# Files
if __name__ == "__main__":
    # Set your directories here
    input_dir = "/jatos_results_data_20250826/filtered_jsons"     # Directory with your filtered JSON files
    output_dir = "/jatos_results_data_20250826/csv_output"        # Directory where CSV files will be saved

    
    # Alternative: if your filtered files are in current directory
    # input_dir = "."
    # output_dir = "csv_results"
    
    process_json_files_to_csv(input_dir, output_dir)
    
    print(f"\nCSV files created in {output_dir}/")
    print("You should now have:")
    print("- ranking_data.csv (for condition_group: ranking)")
    print("- direction_data.csv (for condition_group: direction)")
