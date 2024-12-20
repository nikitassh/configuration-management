import unittest
from main import transform_input_text

class TestParseInput(unittest.TestCase):
    def test_single_line_comment(self):
        input_text = "x = 20  :: этот комментарий игнорируется"
        expected_output = "x = 20  # этот комментарий игнорируется"
        self.assertEqual(transform_input_text(input_text), expected_output)

    def test_multiline_comment(self):
        input_text = """--[[Это многострочный\nкомментарий для теста]]"""
        expected_output = "# Это многострочный\n# комментарий для теста"
        self.assertEqual(transform_input_text(input_text), expected_output)

    def test_constant_declaration(self):
        input_text = "def E := 2.71828;"
        expected_output = "E = 2.71828"
        self.assertEqual(transform_input_text(input_text), expected_output)

    def test_constants_in_dict(self):
        input_text = """dict(\nlength = 15,\n\t width = 5.6)"""
        expected_output = "[[dict]]\nlength = 15\nwidth = 5.6"
        self.assertEqual(transform_input_text(input_text), expected_output)

    def test_dict_parsing(self):
        input_text = "dict(item1=apple, item2=orange)"
        expected_output = "[[dict]]\nitem1 = apple\nitem2 = orange"
        self.assertEqual(transform_input_text(input_text), expected_output)

    def test_ignore_empty_lines(self):
        input_text = "size = 100\n\n\n"
        expected_output = "size = 100"
        self.assertEqual(transform_input_text(input_text), expected_output)

    def test_combined_case(self):
        input_text = """:: Простой комментарий
        def RADIUS := 7;
        dict(item1=box, item2=$RADIUS$)"""
        expected_output = """# Простой комментарий
RADIUS = 7
[[dict]]
item1 = box
item2 = 7"""
        self.assertEqual(transform_input_text(input_text), expected_output)


if __name__ == "__main__":
    unittest.main()
