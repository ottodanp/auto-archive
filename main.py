from os import listdir, mkdir
from os.path import isfile, join
from typing import List, Optional
from threading import Thread


class Item:
    _name: str
    _directory: str
    _path: str
    _is_file: bool

    def __init__(self, name: str, directory: str):
        self._name = name
        self._directory = directory
        self._path = join(directory, name)
        self._is_file = isfile(self._path)

    def read_contents(self) -> Optional[bytes]:
        if not self._is_file:
            return None
        with open(self._path, 'rb') as file:
            return file.read()

    @property
    def name(self) -> str:
        return self._name

    @property
    def directory(self) -> str:
        return self._directory

    @property
    def path(self) -> str:
        return self._path

    @property
    def is_file(self) -> bool:
        return self._is_file

    @property
    def extension(self) -> Optional[str]:
        return self._name.split('.')[-1] if self._is_file else None


def get_items(directory: str) -> List[Item]:
    return [Item(item, directory) for item in listdir(directory)]


def group_files(items: List[Item]) -> dict:
    files = {}
    for item in items:
        if not item.is_file:
            continue
        if item.extension not in files:
            files[item.extension] = [item]
            continue
        files[item.extension].append(item)

    return files


def move_file(file: Item, output_folder: str) -> None:
    new_path = join(output_folder, file.name)
    with open(new_path, 'wb') as new_file:
        new_file.write(file.read_contents())


def move_grouped_files(grouped_files: dict, output_folder: str) -> None:
    for file_type, files in grouped_files.items():
        folder_path = join(output_folder, file_type)
        mkdir(folder_path)
        for file in files:
            Thread(target=move_file, args=(file, folder_path,)).start()


def move_all_files(items: List[Item], output_folder: str, archive_folders: bool) -> None:
    for item in items:
        if not item.is_file and not archive_folders:
            continue

        if item.is_file:
            Thread(target=move_file, args=(item, output_folder,)).start()
            continue

        new_path = join(output_folder, item.name)
        mkdir(new_path)
        move_all_files(get_items(item.path), new_path, archive_folders)


def archive(do_group_files: bool, archive_folders: bool, directory: str, output_folder: str,
            archive_name: Optional[str] = None) -> None:
    archive_name = directory.split('/')[-1].lower() if not archive_name else archive_name
    archive_path = join(output_folder, archive_name)
    mkdir(archive_path)

    items = get_items(directory)
    if do_group_files:
        grouped_files = group_files(items)
        move_grouped_files(grouped_files, archive_path)

    else:
        move_all_files(items, archive_path, archive_folders)


if __name__ == '__main__':
    archive(True, True, 'C:/Users/ottod/Downloads', 'C:/Users/ottod/Downloads')
