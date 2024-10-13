def merge_and_replace_code_tables(text):
    lines = text.split('\n')
    output_lines = []
    in_code_block = False
    code_block_lines = []
    is_table_code_block = False

    for line in lines:
        stripped_line = line.strip()
        start_code_block = stripped_line == '` | | | | --- | --- |'
        end_code_block = stripped_line == '`'

        if in_code_block and end_code_block:
            in_code_block = False
            if is_table_code_block:
                code_lines = []
                for code_line in code_block_lines:
                    if '|' in code_line:
                        parts = code_line.split('|')
                        if len(parts) > 2:
                            code_lines.append(parts[2].strip())
                output_lines.append('```')
                output_lines.extend(code_lines)
                output_lines.append('```')
            else:
                output_lines.append('```')
                output_lines.extend(code_block_lines)
                output_lines.append('```')
        elif start_code_block:
            if not in_code_block:
                # Start of a code block
                in_code_block = True
                code_block_lines = []
                is_table_code_block = False
            else:
                # End of a code block
                in_code_block = False
                if is_table_code_block:
                    # Process the code block as a table
                    code_lines = []
                    for code_line in code_block_lines:
                        if '|' in code_line:
                            parts = code_line.split('|')
                            if len(parts) > 2:
                                # Extract the code part (third column)
                                code_lines.append(parts[2].strip())
                    # Replace with triple backticks and the code content
                    output_lines.append('```')
                    output_lines.extend(code_lines)
                    output_lines.append('```')
                else:
                    # Not a table; replace single backticks with triple backticks
                    output_lines.append('```')
                    output_lines.extend(code_block_lines)
                    output_lines.append('```')
        else:
            if in_code_block:
                code_block_lines.append(line)
                if '|' in line and line.strip():
                    is_table_code_block = True
            else:
                output_lines.append(line)

    # Handle unclosed code block at the end of the text
    if in_code_block:
        if is_table_code_block:
            code_lines = []
            for code_line in code_block_lines:
                if '|' in code_line:
                    parts = code_line.split('|')
                    if len(parts) > 2:
                        code_lines.append(parts[2].strip())
            output_lines.append('```')
            output_lines.extend(code_lines)
            output_lines.append('```')
        else:
            output_lines.append('```')
            output_lines.extend(code_block_lines)
            output_lines.append('```')

    result = '\n'.join(output_lines)
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
