import json
import os
import glob

def check_all_attention_passed(data):
    """
    Check if all attention check questions in the JSON data have passed=true
    Returns True if all attention checks passed, False otherwise
    """
    attention_checks = []
    
    # Find all attention check questions
    for response in data.get('responses', []):
        if isinstance(response.get('question'), str) and response['question'].startswith('attention_check_'):
            attention_checks.append(response)
    
    # Check if we found any attention checks
    if not attention_checks:
        print(f"Warning: No attention checks found in file")
        return False
    
    # Check if all attention checks passed
    all_passed = all(check.get('passed') == True for check in attention_checks)
    
    print(f"Found {len(attention_checks)} attention checks, all passed: {all_passed}")
    return all_passed

def filter_json_files(input_directory, output_directory):
    """
    Filter JSON files to keep only those where all attention checks passed
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Find all JSON files in input directory
    json_files = glob.glob(os.path.join(input_directory, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {input_directory}")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    passed_count = 0
    failed_count = 0
    
    for file_path in json_files:
        try:
            # Read the JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            filename = os.path.basename(file_path)
            print(f"\nProcessing: {filename}")
            
            # Check if all attention checks passed
            if check_all_attention_passed(data):
                # Copy file to output directory
                output_path = os.path.join(output_directory, filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✓ Copied to output directory")
                passed_count += 1
            else:
                print(f"✗ Skipped (failed attention checks)")
                failed_count += 1
                
        except json.JSONDecodeError as e:
            print(f"Error reading {filename}: Invalid JSON - {e}")
            failed_count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            failed_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Total files processed: {len(json_files)}")
    print(f"Files with all attention checks passed: {passed_count}")
    print(f"Files excluded: {failed_count}")
    print(f"Filtered files saved to: {output_directory}")

# Example usage
if __name__ == "__main__":
    # Set your input and output directories here
    input_dir = "/Users/elifkara/Desktop/jatos_results_data_20250826/input_jsons"      # Directory containing your JSON files
    output_dir = "/Users/elifkara/Desktop/jatos_results_data_20250826/filtered_jsons"  # Directory where filtered files will be saved
    
    # Alternative: Process files in current directory
    # input_dir = "."
    # output_dir = "filtered_results"
    
    filter_json_files(input_dir, output_dir)
    