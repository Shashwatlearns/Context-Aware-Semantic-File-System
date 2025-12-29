from context_engine.context_builder import process_documents

DATA_FOLDER = "../data/sample_files"

def main():
    contexts = process_documents(DATA_FOLDER)

    print("\n===== CONTEXT ENGINE OUTPUT =====\n")

    for c in contexts:
        print(f"File: {c['name']}")
        print(f"  Topic: {c['topic']}")
        print(f"  Category: {c['category']}")
        print(f"  Preview: {c['preview']}\n")

if __name__ == "__main__":
    main()
