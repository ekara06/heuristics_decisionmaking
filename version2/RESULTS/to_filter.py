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
    
    # Bu satır, input_directory'nin TÜM ALT KLASÖRLERİNE bakarak 'data.json' dosyalarını bulur.
    search_pattern = os.path.join(input_directory, '**', 'data.json')
    json_files = glob.glob(search_pattern, recursive=True)
    
    if not json_files:
        # Hata mesajını daha anlaşılır hale getirelim
        print(f"'{input_directory}' klasörü ve alt klasörlerinde 'data.json' adında hiçbir dosya bulunamadı.")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    passed_count = 0
    failed_count = 0
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Her dosyanın adı 'data.json' olacağı için, üst klasörünün adını kullanarak
            # daha anlamlı ve eşsiz bir çıktı dosyası adı oluşturalım.
            parent_dir_name = os.path.basename(os.path.dirname(file_path))
            unique_filename = f"{parent_dir_name}_data.json"
            
            print(f"\nProcessing: {file_path}")
            
            if check_all_attention_passed(data):
                output_path = os.path.join(output_directory, unique_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✓ Copied to output as {unique_filename}")
                passed_count += 1
            else:
                print(f"✗ Skipped (failed attention checks)")
                failed_count += 1
                
        except json.JSONDecodeError as e:
            print(f"Error reading {file_path}: Invalid JSON - {e}")
            failed_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            failed_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Total files processed: {len(json_files)}")
    print(f"Files with all attention checks passed: {passed_count}")
    print(f"Files excluded: {failed_count}")
    print(f"Filtered files saved to: {output_directory}")

# Example usage
if __name__ == "__main__":
    # Arama desenini (**/data.json) buradan siliyoruz.
    input_dir = "/Users/elifkara/Desktop/Helmholtz/RESULTS/json_output/ranking_data"
    output_dir = "/Users/elifkara/Desktop/Helmholtz/RESULTS/filtered_jsons/filtered_ranking"
    
    filter_json_files(input_dir, output_dir)