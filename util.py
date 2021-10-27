import os

excluded_prefixes = ('.', '_', '@')
known_countries = {'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE',
                   'ES', 'FR', 'GR', 'HR', 'IS', 'IT', 'LU', 'LV',
                   'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'}


def walk_path(root_dir: str, country: str) -> list[str]:
    files = []
    country_dir = os.path.join(root_dir, country)
    for dirpath, dirnames, filenames in os.walk(country_dir):
        dirnames[:] = [dirname for dirname in dirnames if not dirname.startswith(excluded_prefixes)]
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return files


def list_country_directories(root_directory: str):
    dirs = []
    for a, dirnames, b in os.walk(root_directory):
        for directory in dirnames:
            if len(directory) == 2:
                dirs.append(directory)
        break
    return dirs
