import subprocess
import json
import os
import yaml
import sys

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_package_dependencies(package_name):
    result = subprocess.run(
        ['npm', 'show', package_name, 'dependencies', '--json'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Ошибка при получении зависимостей: {result.stderr}")
    
    if not result.stdout.strip():
        return {}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise Exception(f"Ошибка при парсинге JSON для зависимостей {package_name}: {result.stdout}")

def parse_dependencies(dependencies, package_name, depth, max_depth):
    if depth > max_depth:
        return ""
    
    graph = ""
    for dep, version in dependencies.items():
        dep_name = dep
        dep_version = version
        graph += f"  {package_name} --> {dep_name}({dep_version})\n"
        nested_deps = get_package_dependencies(dep_name)
        graph += parse_dependencies(nested_deps, dep_name, depth + 1, max_depth)
    
    return graph

def generate_mermaid_graph(dependencies_graph):
    return f"graph TD\n{dependencies_graph}"

def save_graph_to_file(graph, file_path):
    with open(file_path, 'w') as file:
        file.write(graph)

def generate_graph_image(input_file, output_file, visualizer_path):
    subprocess.run([visualizer_path, '-i', input_file, '-o', output_file])

def visualize_dependencies():
    config = load_config('config.yaml')
    
    data = get_package_dependencies(config['package_name'])
    
    if not data:
        print(f"Нет зависимостей для пакета {config['package_name']}")
        return
    
    dependencies_graph = parse_dependencies(data, config['package_name'], 1, config['max_depth'])
    mermaid_graph = generate_mermaid_graph(dependencies_graph)
    
    temp_file_path = 'temp.mmd'
    save_graph_to_file(mermaid_graph, temp_file_path)
    
    generate_graph_image(temp_file_path, config['output_image_path'], config['visualizer_path'])

if __name__ == "__main__":
    visualize_dependencies()
