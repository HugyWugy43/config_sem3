import unittest
from unittest.mock import MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from emulator import VirtualFileSystem, ShellEmulator


# Мокируем VirtualFileSystem для тестирования
class MockVirtualFileSystem:
    def __init__(self, zip_file):
        # Мокаем файлы в виртуальной файловой системе
        self.filesystem = [
            'fs_image/',
            'fs_image/dir1/',
            'fs_image/dir1/test1.txt',
            'fs_image/dir2/',
            'fs_image/dir2/test2.txt',
            'fs_image/test.txt',
        ]
        self.current_path = "/"

    def list_directory(self, path):
        # Возвращаем список файлов и директорий для тестируемого пути
        files = [f[len(path):].split('/')[0] for f in self.filesystem if f.startswith(path)]
        return sorted(set(f for f in files if f))  # Убираем дубли

    def resolve_path(self, path):
        if path.startswith("/"):
            return path
        else:
            return os.path.normpath(os.path.join(self.current_path, path)) + "/"

    def change_directory(self, path):
        self.current_path = path


class TestShellCommands(unittest.TestCase):

    def setUp(self):
        # Мокируем VirtualFileSystem и ShellEmulator
        self.fs = MockVirtualFileSystem('mock.zip')
        self.shell = ShellEmulator(username="testuser", zip_file="mock.zip")
        self.shell.fs = self.fs
        self.shell.output_area = MagicMock()  # Мокаем вывод в консоль

    def test_cd_valid_directory(self):
        # Проверяем команду cd с правильным путем
        self.shell.process_command("cd fs_image/dir1")
        self.assertEqual(self.fs.current_path, "/fs_image/dir1")
        self.shell.output_area.insert.assert_not_called()  # Не должно быть ошибок

    def test_cd_invalid_directory(self):
        # Проверяем команду cd с неправильным путем
        self.shell.process_command("cd non_existent_dir")
        self.assertTrue(self.shell.output_area.insert.called)  # Ожидаем сообщение об ошибке

    def test_cd_back_to_root(self):
        # Проверяем переход обратно в корневую директорию
        self.fs.current_path = "/fs_image/dir1"
        self.shell.process_command("cd /")
        self.assertEqual(self.fs.current_path, "/")
        self.shell.output_area.insert.assert_not_called()  # Не должно быть ошибок

    def test_ls_current_directory(self):
        # Проверяем команду ls для текущей директории
        self.fs.current_path = "/fs_image"
        self.shell.process_command("ls")
        # Ожидаем вывод файлов в текущей директории fs_image
        self.shell.output_area.insert.assert_called_with(MagicMock(), "dir1\ndir2\ntest.txt\n")

    def test_ls_empty_directory(self):
        # Проверяем команду ls для пустой директории
        self.fs.current_path = "/fs_image/dir1"
        self.shell.process_command("ls")
        # Ожидаем вывод пустой директории (поскольку нет файлов в dir1)
        self.shell.output_area.insert.assert_called_with(MagicMock(), "test1.txt\n")

    def test_ls_no_files(self):
        # Проверяем команду ls в случае, если в директории нет файлов
        self.fs.current_path = "/fs_image/dir2"
        self.shell.process_command("ls")
        # Ожидаем вывод пустой директории (поскольку нет файлов в dir2)
        self.shell.output_area.insert.assert_called_with(MagicMock(), "test2.txt\n")

    def test_ls_with_no_files_in_directory(self):
        # Проверяем команду ls для директории, в которой нет файлов
        self.fs.current_path = "/non_existent_dir"
        self.shell.process_command("ls")
        self.shell.output_area.insert.assert_called_with(MagicMock(), "Directory is empty.\n")


if __name__ == '__main__':
    unittest.main()
