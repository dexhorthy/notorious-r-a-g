import os
import json
from tqdm import tqdm
from test_script import html_to_markdown

def process_crawled_docs():
    crawled_docs_dir = os.path.join(os.path.dirname(__file__), 'crawled_docs')
    fixed_docs_dir = os.path.join(os.path.dirname(__file__), 'fixed_docs')

    # Create the fixed_docs directory if it doesn't exist
    os.makedirs(fixed_docs_dir, exist_ok=True)

    for filename in tqdm(os.listdir(crawled_docs_dir), desc="Processing files"):
        if filename.endswith('.json'):
            file_path = os.path.join(crawled_docs_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                doc = json.load(f)

                if 'markdown' in doc and doc['metadata']['statusCode'] != 404:
                    doc['markdown'] = doc['markdown'].replace('` | | | | --- | --- | ', '`   |     |     | | --- | --- |\n')
                    # Fix the markdown content
                    fixed_markdown = html_to_markdown(doc['html'])
                    
                    # Update the document with fixed markdown
                    doc['markdown'] = fixed_markdown
                    
                    # Save the fixed document
                    fixed_file_path = os.path.join(fixed_docs_dir, filename)
                    with open(fixed_file_path, 'w', encoding='utf-8') as f_out:
                        json.dump(doc, f_out, ensure_ascii=False, indent=2)

    print(f"Processed and fixed markdown for all documents. Results saved in {fixed_docs_dir}")

if __name__ == "__main__":
    process_crawled_docs()
