import os

def check_file_bytes(filepath, pos):
    if not os.path.exists(filepath):
        print(f"{filepath} not found")
        return
    with open(filepath, 'rb') as f:
        data = f.read()
    print(f"\nFile: {filepath}, Size: {len(data)} bytes")
    print(f"Bytes around position {pos}:")
    start = max(0, pos - 20)
    end = min(len(data), pos + 20)
    sub = data[start:end]
    print(f"  Hex: {sub.hex(' ')}")
    print(f"  Raw: {sub}")
    # Show character in utf-8
    try:
        print(f"  UTF-8 decoded context: {sub.decode('utf-8')}")
    except Exception as e:
        print(f"  UTF-8 decode failed: {e}")

if __name__ == '__main__':
    check_file_bytes('unpacked_ta_proyek/word/document.xml', 3413)
    check_file_bytes('unpacked_ta_proyek/word/numbering.xml', 3338)
