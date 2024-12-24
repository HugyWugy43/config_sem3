import unittest
from pathlib import Path
import subprocess

from visualizer import build_dependency_graph, generate_mermaid_graph, convert_mermaid_to_png

class TestGitDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.test_repo = Path(r'C:\Users\Admin\proj\con_2')
        if not (self.test_repo / '.git').exists():
            subprocess.run(['git', 'init'], cwd=self.test_repo, check=True)
            # Добавьте начальный коммит для тестов
            (self.test_repo / 'file1.txt').write_text('Initial content')
            result = subprocess.run(['git', 'log', '--oneline'], cwd=self.test_repo, stdout=subprocess.PIPE, text=True)
            print("Git log:", result.stdout)

            subprocess.run(['git', 'add', 'file1.txt'], cwd=self.test_repo, check=True)
            result = subprocess.run(['git', 'log', '--oneline'], cwd=self.test_repo, stdout=subprocess.PIPE, text=True)
            print("Git log:", result.stdout)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=self.test_repo, check=True)
            result = subprocess.run(['git', 'log', '--oneline'], cwd=self.test_repo, stdout=subprocess.PIPE, text=True)
            print("Git log:", result.stdout)


    def run_git_command(self, args):
        result = subprocess.run(['git'] + args, cwd=self.test_repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            self.fail(f"Git команда не выполнена: {' '.join(args)}\nОшибка: {result.stderr}")
        return result.stdout.strip()

    def test_full_flow(self):
        # Получение всех коммитов
        commits = self.run_git_command(['rev-list', '--max-parents=0', 'HEAD']).split('\n')
        graph, file_nodes = build_dependency_graph(self.test_repo, commits)
    
        # Проверка корректности графа
        print("file_nodes содержат:", file_nodes)  # Для отладки
        self.assertIn('file_file1.txt', file_nodes)  # Убедитесь, что имя файла корректно

        # Путь к выходным файлам
        mermaid_path = self.test_repo / 'output.mmd'
        png_path = self.test_repo / 'output.png'
        viz_program = "mmdc"  # Путь к программе для визуализации (замените на полный путь, если требуется)

        # Генерация графа Mermaid
        generate_mermaid_graph(graph, file_nodes, output_mermaid_path=mermaid_path)
        self.assertTrue(mermaid_path.exists())  # Проверка существования файла

        # # Генерация PNG-изображения из Mermaid
        # convert_mermaid_to_png(viz_program, str(mermaid_path), str(png_path))
        # self.assertTrue(png_path.exists())  # Проверка существования PNG-файла



    def test_generate_mermaid_graph(self):
        graph = {"commit_somehash": {"file_file1.txt"}}  # Предположим, что вы подготовили граф
        mermaid_path = self.test_repo / 'output.mmd'
        generate_mermaid_graph(graph, {'file1.txt'}, output_mermaid_path=mermaid_path)
        self.assertTrue(mermaid_path.exists())
        # Дополнительные проверки содержимого файла

    def generate_graph_image(mmd_path: Path, png_path: Path):
        try:
            subprocess.run(['mmdc', '-i', str(mmd_path), '-o', str(png_path)], check=True)
            print(f"Граф коммитов сохранен как {png_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при генерации изображения: {e}")
    
    def test_get_commit_hashes(self):
        commit_hash = self.run_git_command(['rev-list', '--max-parents=0', 'HEAD'])
        self.assertTrue(commit_hash)  # Проверка, что хэш не пустой

if __name__ == '__main__':
    unittest.main()