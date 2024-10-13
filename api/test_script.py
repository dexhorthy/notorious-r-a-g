import re

def merge_and_replace_code_tables(text):
    def merge_code(match):
        # Extract the content between the backticks
        code_block = match.group(1)
        lines = code_block.strip('\n').split('\n')

        # Check if the code block is a table (contains lines starting with '|')
        if all('|' in line for line in lines if line.strip()):
            # Process lines that are part of the table
            code_lines = []
            for line in lines:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) > 2:
                        # Get the code part from the third column (index 2)
                        part: str = parts[2]

                        code_lines.append(part.rstrip())
            # Return the merged code block with triple backticks
            return '```\n' + '\n'.join(code_lines) + '\n```'
        else:
            # If not a table, replace single backticks with triple backticks
            return '```\n' + code_block + '\n```'

    # Pattern to match code blocks inside backticks, non-greedy
    pattern = r'`(.*?)`'

    # Use re.DOTALL to handle multiline code blocks
    result = re.sub(pattern, merge_code, text, flags=re.DOTALL)

    return result

if __name__ == '__main__':
    # Example usage
    input_text = """
    Some text before the code block.

    If you have to declare a list in a .baml file you can use this syntax:
    ` | | | | --- | --- |
    | 1 | { |
    | 2 |   key1 [value1, value2, value3], |
    | 3 | key2 [ |
    | 4 | value1, |
    | 5 | value2, |
    | 6 | value3 |
    | 7 | ] |
    | 8 | key3 [ |
    | 9 | { |
    | 10 | key1 value1, |
    | 11 | key2 value2 |
    | 12 | }, |
    | 13 | { |
    | 14 | key1 value1, |
    | 15 | key2 value2 |
    | 16 | } |
    | 17 | ] |
    | 18 | } |
    `
    The commas are optional if doing a multiline list.

    Here's another example:
    `
    | 1 | def example(): |
    | 2 |     print("Hello, World!") |
    `

    End of the examples.
    """

    result = merge_and_replace_code_tables(input_text)
    print(result)
