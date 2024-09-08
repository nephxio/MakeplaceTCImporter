import json
import base64
import webbrowser
from tkinter import filedialog
from typing import Optional, IO, Dict, List, Tuple, Any
from dye_data import dye_data


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


def get_teamcraft_list_url(import_string: str, callback_url: Optional[str] = None) -> None:
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


def write_item_lists_to_file(item_list: Dict[str, List[int]], import_string: str,
                             dye_list: Optional[Dict[str, int]] = None) -> None:
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
            file.write('Shopping List\n')
            file.write('----------------\n')
            for item, count in item_list.items():
                file.write(f'{item} x{count[1]}\n')


def extract_makeplace_items() -> Tuple[Dict[str, Any], str]:
    """
    Extracts items from a Makeplace file.

    Returns:
        Dict[str, Any]: Dictionary of items and their counts.
    """
    makeplace_data = load_makeplace_file()
    makeplace_items: Dict[str, List[int]] = {}
    teamcraft_import_string = ''

    def process_item(item: Dict[str, Any]) -> None:
        item_name = item.get('name', 'Unknown')
        item_id = int(item['itemId'])

        # Discard items with an itemId of 0
        if item_id == 0:
            return

        color_value = item.get('properties', {}).get('color', '')[
                      :6]  # Extract the color value without the alpha channel

        if color_value and color_value in dye_data:
            color_id = dye_data[color_value][1]
            if item_name in makeplace_items:
                makeplace_items[item_name][1] += 1
            else:
                makeplace_items[item_name] = [item_id, 1]

            color_name = f"{dye_data[color_value][0]}"
            if color_name in makeplace_items:
                makeplace_items[color_name][1] += 1
            else:
                makeplace_items[color_name] = [color_id, 1]
        else:
            if item_name in makeplace_items:
                makeplace_items[item_name][1] += 1
            else:
                makeplace_items[item_name] = [item_id, 1]

    for int_fixture in makeplace_data.get('interiorFixture', []):
        process_item(int_fixture)

    for ext_fixture in makeplace_data.get('interiorFixture', []):
        process_item(ext_fixture)

    for int_furniture in makeplace_data.get('interiorFurniture', []):
        process_item(int_furniture)

    for ext_furniture in makeplace_data.get('exteriorFurniture', []):
        process_item(ext_furniture)

    item_count = len(makeplace_items)
    for index, (key, value) in enumerate(makeplace_items.items()):
        teamcraft_import_string += f"{value[0]},null,{value[1]}"
        if index < item_count - 1:
            teamcraft_import_string += ";"

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
