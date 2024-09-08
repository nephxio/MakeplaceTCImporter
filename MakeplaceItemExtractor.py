import json
import base64
import webbrowser
from tkinter import filedialog
from typing import Optional, IO, Dict, List, Tuple, Any


def main() -> None:
    """
    Main function to extract items from a Makeplace file and write them to a text file.
    """
    makeplace_items, teamcraft_import_string = extract_makeplace_items()
    write_item_lists_to_file(makeplace_items, teamcraft_import_string)
    get_teamcraft_list_url(teamcraft_import_string)


def construct_teamcraft_url(import_string: str, callback_url: Optional[str] = None) -> str:
    """
    Constructs the URL for importing items into FFXIV Teamcraft.

    Args:
        import_string (str): The import string in the format specified.
        callback_url (Optional[str]): The callback URL to be notified once the list is created.

    Returns:
        str: The constructed URL.
    """
    # Encode the import string in base64
    encoded_string = base64.b64encode(import_string.encode()).decode()

    # Construct the base URL
    url = f"https://ffxivteamcraft.com/import/{encoded_string}"

    # Append the callback URL if provided
    if callback_url:
        url += f"?callback={callback_url}"

    return url


def get_teamcraft_list_url(import_string: str, callback_url: Optional[str] = None) -> str:
    """
    Makes an HTTP request to the Teamcraft import URL and returns the resulting list URL.

    Args:
        import_string (str): The import string in the format specified.
        callback_url (Optional[str]): The callback URL to be notified once the list is created.

    Returns:
        str: The resulting list URL.
    """
    # Construct the Teamcraft URL
    teamcraft_url = construct_teamcraft_url(import_string, callback_url)

    # Open the URL in a new browser tab
    webbrowser.open_new_tab(teamcraft_url)
    print("URL opened in a new browser tab.")


def write_item_lists_to_file(item_list: Dict[str, int], import_string: str, dye_list: Optional[Dict[str, int]] = None) -> None:
    """
    Writes item lists to a file selected by the user.

    Args:
        item_list (Dict[str, int]): Dictionary of items and their counts.
        import_string (str): Teamcraft import string.
        dye_list (Optional[Dict[str, int]]): Dictionary of dyes and their counts, optional.
    """
    file_handle = filedialog.asksaveasfile(mode='w', defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

    if file_handle:
        with file_handle as file:
            file.write('Artisan Import String\n')
            file.write('----------------\n')
            file.write(import_string)

            file.write('\n\n')

            file.write('Artisan List\n')
            file.write('----------------\n')
            for key, value in item_list.items():
                for _ in range(value[1]):
                    file.write(f'{key}\n')

            file.write('\n\n')

            file.write('Makeplace Items\n')
            file.write('----------------\n')
            for item, count in item_list.items():
                file.write(f'{item}: {count}\n')

            file.write('\n\n')

            if dye_list is not None:
                file.write('Makeplace Dyes\n')
                file.write('----------------\n')
                for dye, count in dye_list.items():
                    file.write(f'{dye}: {count}\n')


def extract_makeplace_items() -> Tuple[Dict[str, Any], str]:
    """
    Extracts items from a Makeplace file.

    Returns:
        Dict[str, Any]: Dictionary of items and their counts.
    """
    makeplace_data = load_makeplace_file()
    makeplace_items: Dict[str, List[int]] = {}
    makeplace_dyes: Dict[str, int] = {}
    teamcraft_import_string = ''

    for item in makeplace_data.get('interiorFurniture', []):
        item_name = item.get('name', 'Unknown')
        if item_name in makeplace_items:
            makeplace_items[item_name][1] += 1
        else:
            makeplace_items[item_name] = [int(item['itemId']), 1]

    item_count = len(makeplace_items)
    for index, (key, value) in enumerate(makeplace_items.items()):
        teamcraft_import_string += f"{value[0]},null,{value[1]}"
        if index < item_count - 1:
            teamcraft_import_string += ";"

    print(teamcraft_import_string)
    return makeplace_items, teamcraft_import_string


def load_makeplace_file() -> Dict[str, Any]:
    """
    Loads a Makeplace file selected by the user.

    Returns:
        Dict[str, Any]: Data from the Makeplace file.
    """
    file_handle = display_file_open_dialog()
    makeplace_data = json.load(file_handle)
    file_handle.close()
    return makeplace_data


def display_file_open_dialog() -> Optional[IO]:
    """
    Displays a file open dialog for the user to select a file.

    Returns:
        Optional[IO]: File handle of the selected file.

    Raises:
        FileNotFoundError: If no file is selected.
    """
    try:
        file_handle = filedialog.askopenfile(mode='r', filetypes=[('JSON files', '*.json')])
        if file_handle:
            return file_handle
        else:
            raise FileNotFoundError("No file selected")
    except FileNotFoundError as e:
        print(e)
        return None


if __name__ == "__main__":
    main()