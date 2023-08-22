import json
from pathlib import Path

OUPUT_DIR = Path(__file__).resolve().parent.parent


def read_json(file_path: str) -> dict:

    """Reads and parses data from a JSON file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the JSON data cannot be decoded.
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error decoding JSON in '{file_path}': {e}", e.doc, e.pos)


def write_file(file_name: str, words_list: list,
               output_dir=OUPUT_DIR/'result_Data'):

    """Writes a list of words to a text file.
    """

    try:
        with open(str(output_dir / file_name), 'w') as f:
            list = words_list
            formatted_list = {f"{item}\n" for item in list}
            f.writelines(formatted_list)
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory '{output_dir}' not found.")