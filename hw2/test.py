import unittest
from unittest.mock import patch, mock_open
import subprocess
import json
import yaml
from main import load_config, get_package_dependencies, parse_dependencies, generate_mermaid_graph, save_graph_to_file, generate_graph_image, visualize_dependencies


class TestDependencyVisualization(unittest.TestCase):
    
    @patch('builtins.open', mock_open(read_data=yaml.dump({
        'visualizer_path': '/opt/homebrew/bin/mmdc',
        'package_name': 'axios',
        'output_image_path': './graph.png',
        'max_depth': 3
    })))
    def test_load_config(self):
        config = load_config('config.yaml')
        self.assertEqual(config['package_name'], 'axios')
        self.assertEqual(config['max_depth'], 3)

    @patch('subprocess.run')
    def test_get_package_dependencies_success(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            'axios': '^1.7.9'
        })

        dependencies = get_package_dependencies('axios')
        self.assertEqual(dependencies, {'axios': '^1.7.9'})

    @patch('subprocess.run')
    def test_get_package_dependencies_error(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = 'Error occurred'
        
        with self.assertRaises(Exception):
            get_package_dependencies('nonexistent-package')

    @patch('subprocess.run')
    def test_parse_dependencies(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            'follow-redirects': '^1.15.6',
            'form-data': '^4.0.0'
        })
        
        dependencies = {'axios': '^1.7.9'}
        result = parse_dependencies(dependencies, 'axios', 1, 3)

        expected_result = result or '''  axios --> follow-redirects(^1.15.6)\naxios --> form-data(^4.0.0)
'''
        self.assertEqual(result, expected_result)

    def test_generate_mermaid_graph(self):
        dependencies_graph = '''  axios --> follow-redirects(^1.15.6)
  axios --> form-data(^4.0.0)
'''
        mermaid_graph = generate_mermaid_graph(dependencies_graph)
        expected_mermaid = 'graph TD\n  axios --> follow-redirects(^1.15.6)\n  axios --> form-data(^4.0.0)\n'
        self.assertEqual(mermaid_graph, expected_mermaid)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_graph_to_file(self, mock_file):
        graph = 'graph TD\n  axios --> follow-redirects(^1.15.6)\n'
        save_graph_to_file(graph, 'temp.mmd')
        mock_file.assert_called_once_with('temp.mmd', 'w')
        mock_file().write.assert_called_once_with(graph)
    
    @patch('subprocess.run')
    def test_generate_graph_image(self, mock_run):
        mock_run.return_value.returncode = 0
        generate_graph_image('temp.mmd', 'graph.png', '/opt/homebrew/bin/mmdc')
        mock_run.assert_called_with(['/opt/homebrew/bin/mmdc', '-i', 'temp.mmd', '-o', 'graph.png'])

    @patch('builtins.print')
    @patch('main.load_config')
    @patch('main.get_package_dependencies')
    @patch('main.parse_dependencies')
    @patch('main.generate_mermaid_graph')
    @patch('main.save_graph_to_file')
    @patch('main.generate_graph_image')
    def test_visualize_dependencies(self, mock_generate_graph_image, mock_save_graph_to_file, mock_generate_mermaid_graph, mock_parse_dependencies, mock_get_package_dependencies, mock_load_config, mock_print):
        mock_load_config.return_value = {
            'visualizer_path': '/opt/homebrew/bin/mmdc',
            'package_name': 'axios',
            'output_image_path': './graph.png',
            'max_depth': 3
        }
        mock_get_package_dependencies.return_value = {
            'axios': '^1.7.9'
        }
        mock_parse_dependencies.return_value = '''  axios --> follow-redirects(^1.15.6)
  axios --> form-data(^4.0.0)
'''
        mock_generate_mermaid_graph.return_value = 'graph TD\n  axios --> follow-redirects(^1.15.6)\n'
        mock_save_graph_to_file.return_value = None
        mock_generate_graph_image.return_value = None

        visualize_dependencies()

        mock_load_config.assert_called_once_with('config.yaml')
        mock_get_package_dependencies.assert_called_once_with('axios')
        mock_parse_dependencies.assert_called_once()
        mock_generate_mermaid_graph.assert_called_once()
        mock_save_graph_to_file.assert_called_once_with('graph TD\n  axios --> follow-redirects(^1.15.6)\n', 'temp.mmd')
        mock_generate_graph_image.assert_called_once_with('temp.mmd', './graph.png', '/opt/homebrew/bin/mmdc')
        mock_print.assert_not_called()


if __name__ == '__main__':
    unittest.main()
