#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import sys
from collections import defaultdict
import logging

logging.basicConfig(level=logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Инструмент для визуализации графа зависимостей Git-репозитория.')
    parser.add_argument('--viz_program', required=True, help='Путь к программе для визуализации графов (например, mmdc).')
    parser.add_argument('--repo_path', required=True, help='Путь к анализируемому Git-репозиторию.')
    parser.add_argument('--output_path', required=True, help='Путь к выходному PNG-файлу графа зависимостей.')
    parser.add_argument('--tag', required=True, help='Имя тега в репозитории.')
    return parser.parse_args()

def run_git_command(repo_path, args):
    try:
        result = subprocess.run(['git'] + args, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        logging.debug(f"Git command succeeded: git {' '.join(args)}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка выполнения команды Git: {e.stderr}")
        raise  # Re-raise the exception to let the caller handle it

def get_commit_hashes(repo_path, tag):
    # Получить все коммиты до указанного тега
    log = run_git_command(repo_path, ['rev-list', tag])
    commits = log.strip().split('\n')
    return commits

import logging

def get_files_changed(repo_path, commit_hash):
    try:
        # Используем правильный формат для подавления вывода
        log = run_git_command(repo_path, ['show', '--pretty=format:', '--name-only', commit_hash])
        files = log.strip().split('\n') if log else []
        filtered_files = [f for f in files if f]
        logging.info(f"Обнаруженные изменённые файлы: {filtered_files}")
        return filtered_files
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении команды Git для коммита {commit_hash}: {e.stderr}")
        return []



def build_dependency_graph(repo_path, commits):
    graph = defaultdict(set)
    file_nodes = set()

    if not commits:
        logging.error("Список коммитов пуст.")
        return graph, file_nodes

    for commit in commits:
        files = get_files_changed(repo_path, commit)
        logging.debug(f"Files changed in commit {commit}: {files}")
        if files is None:
            logging.warning(f"Не удалось получить файлы для коммита {commit}.")
            continue
        logging.debug(f"Коммит {commit} изменил файлы: {files}")
        commit_node = f"commit_{commit}"
        for f in files:
            file_node = f"file_{f.replace('/', '_')}"
            logging.debug(f"Добавляется файл {f} как {file_node}")
            graph[commit_node].add(file_node)
            file_nodes.add(file_node)
    
    logging.info(f"Общее количество файлов в file_nodes: {len(file_nodes)}")
    return graph, file_nodes

def generate_mermaid_graph(graph, file_nodes, output_mermaid_path):
    mermaid = "graph TD;\n"
    for commit, files in graph.items():
        commit_node = f"{commit}"
        for file in files:
            # Заменяем точки на подчёркивания в имени файла
            file_node = f"{file}"
            mermaid += f"    {commit_node} --> {file_node};\n"
    with open(output_mermaid_path, 'w') as f:
        f.write(mermaid)
    return mermaid

def convert_mermaid_to_png(viz_program, mermaid_path, png_path):
    try:
        subprocess.run([viz_program, '-i', mermaid_path, '-o', png_path], check=True)
        print("Визуализация успешно выполнена. PNG-файл сохранен.")
    except subprocess.CalledProcessError as e:
        print("Ошибка при визуализации графа.")
        sys.exit(1)

def main():
    args = parse_arguments()

    # Проверка путей
    if not os.path.isfile(args.viz_program):
        print(f"Программа для визуализации не найдена по пути: {args.viz_program}")
        sys.exit(1)
    if not os.path.isdir(args.repo_path):
        print(f"Репозиторий не найден по пути: {args.repo_path}")
        sys.exit(1)

    commits = get_commit_hashes(args.repo_path, args.tag)
    if not commits:
        print(f"Тег {args.tag} не найден или не содержит коммитов.")
        sys.exit(1)

    graph, file_nodes = build_dependency_graph(args.repo_path, commits)

    # Создание временного файла для Mermaid
    mermaid_path = os.path.join(os.path.dirname(args.output_path), 'graph.mmd')
    generate_mermaid_graph(graph, file_nodes, mermaid_path)

    # Визуализация
    convert_mermaid_to_png(args.viz_program, mermaid_path, args.output_path)

    # Удаление временного файла
    os.remove(mermaid_path)

    print("Граф зависимостей успешно построен и сохранен.")

if __name__ == "__main__":
    main()