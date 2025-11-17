import unittest

# 假设 game_utils.py 中可能有通用函数，例如 clamp(x, low, high)
try:
    import game_utils  # noqa: F401
except ImportError:
    game_utils = None

# 提供一个占位 clamp 实现（如果原文件存在则不使用本地定义逻辑，仅测试示例）
if game_utils and hasattr(game_utils, 'clamp'):
    clamp = game_utils.clamp
else:
    def clamp(x, low, high):
        return low if x < low else high if x > high else x

class TestGameUtils(unittest.TestCase):
    def test_clamp_lower(self):
        self.assertEqual(clamp(-10, 0, 5), 0)

    def test_clamp_upper(self):
        self.assertEqual(clamp(99, 0, 5), 5)

    def test_clamp_middle(self):
        self.assertEqual(clamp(3, 0, 5), 3)

if __name__ == '__main__':
    unittest.main()