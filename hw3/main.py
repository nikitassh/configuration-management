import sys
import re

def transform_input_text(input_text):
    processed_lines = []
    variable_map = {}

    input_text = re.sub(r'::', '#', input_text)

    def replace_multiline_comment(match):
        comment_content = match.group(1).strip()
        return "\n".join([f"# {line}" for line in comment_content.splitlines()])
    
    input_text = re.sub(r'--\[\[(.*?)\]\]', replace_multiline_comment, input_text, flags=re.DOTALL)

    def process_constant(match):
        constant_name = match.group(1).strip()
        constant_value = match.group(2).strip()
        variable_map[constant_name] = constant_value
        return f"{constant_name} = {constant_value}"

    input_text = re.sub(r'set\s+([a-zA-Z_][a-zA-Z0-9]*)\s*=\s*(.*)', process_constant, input_text)

    def handle_dict(match):
        dict_entries = match.group(1).split(',')
        dict_representation = "[[dict]]\n"
        for entry in dict_entries:
            key, value = entry.split('=', 1)
            key = key.strip()
            value = value.strip()

            if value.startswith("$") and value.endswith("$"):
                value = variable_map.get(value[1:-1], value)

            dict_representation += f"{key} = {value}\n"
        return dict_representation.strip()

    input_text = re.sub(r'dict\((.*?)\)', handle_dict, input_text, flags=re.DOTALL)

    for line in input_text.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            processed_lines.append(stripped_line)

    return "\n".join(processed_lines)


def process_files():
    if len(sys.argv) < 3:
        print("Ошибка: недостаточно аргументов. Пожалуйста, укажите пути к исходному и выходному файлам.")
        return

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    try:
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            content = input_file.read()

        transformed_content = transform_input_text(content)

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(transformed_content)

        print(f"Конфигурация успешно преобразована и сохранена в файл: '{output_file_path}'.")

    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file_path}' не найден.")
    except Exception as error:
        print(f"Ошибка: {error}")


if __name__ == "__main__":
    process_files()
