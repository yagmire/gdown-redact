from .download import download
import ast
from bs4 import BeautifulSoup
import requests

client = requests.session()


def download_folder(
    folder, quiet=False, proxy=None, speed=None, use_cookies=True
):
    """Download entire folder from URL.

    Parameters
    ----------
    url: str
        URL of the Google Drive folder.
        Must be of the format 'https://drive.google.com/drive/folders/{url}'.
    quiet: bool, optional
        Suppress terminal output.
    proxy: str, optional
        Proxy.
    speed: float, optional
        Download byte size per second (e.g., 256KB/s = 256 * 1024).
    use_cookies: bool
        Flag to use cookies. Default is True.

    Returns
    -------
    return_code: bool
        Returns False if the download completed unsuccessfully.
        May be due to invalid URLs, permission errors, rate limits, etc.

    Example
    -------
    gdown.download_folder(
        "https://drive.google.com/drive/folders/" +
        "1ZXEhzbLRLU1giKKRJkjm8N04cO_JoYE2",
        use_cookies=True
    )
    """
    return_code = True

    folders_url = "https://drive.google.com/drive/folders/"
    files_url = "https://drive.google.com/uc?id="

    folder_page = client.get(folder)

    if folder_page.status_code != 200:
        return False
    folder_soup = BeautifulSoup(folder_page.text, features="html.parser")

    if not use_cookies:
        client.cookies.clear()
    # finds the script tag with window['_DRIVE_ivd']
    # in it and extracts the encoded array
    byte_string = folder_soup.find_all("script")[-3].contents[0][24:-113]

    # decodes the array and evaluates it as a python array
    folder_arr = ast.literal_eval(
        byte_string.replace("\\/", "/")
        .encode("utf-8")
        .decode("unicode-escape")
        .replace("\n", "")
        .replace("null", '"null"')
    )

    folder_file_list = [i[0] for i in folder_arr[0]]
    folder_name_list = [i[2] for i in folder_arr[0]]
    folder_type_list = [i[3] for i in folder_arr[0]]

    for file in range(len(folder_file_list)):
        if folder_type_list[file] != "application/vnd.google-apps.folder":
            return_code = download(
                files_url + folder_file_list[file],
                output=folder_name_list[file],
                quiet=True,
                proxy=proxy,
                speed=speed,
                use_cookies=use_cookies,
            )
            if not quiet:
                print(
                    files_url + folder_file_list[file], folder_name_list[file]
                )
            if not return_code:
                return return_code
        else:
            if not quiet:
                print(
                    "Processing folder",
                    folder_name_list[file],
                    "(" + folders_url + folder_file_list[file] + ")",
                )
            return_code = download_folder(
                folders_url + folder_file_list[file],
                quiet=quiet,
                proxy=proxy,
                speed=speed,
                use_cookies=use_cookies,
            )
            if not return_code:
                return False
    return True