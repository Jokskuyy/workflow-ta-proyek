import os

def search_files():
    unpacked_dir = 'unpacked_ta'
    occurrences = []
    for root, dirs, files in os.walk(unpacked_dir):
        for file in files:
            if file.endswith('.xml') or file.endswith('.rels'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'Arial' in content:
                            count = content.count('Arial')
                            occurrences.append((os.path.relpath(path, unpacked_dir), count))
                except Exception as e:
                    pass
    print("Files containing 'Arial':")
    for rel_path, count in occurrences:
        print(f"  - {rel_path}: {count} occurrences")

if __name__ == '__main__':
    search_files()
