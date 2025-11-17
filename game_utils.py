# game_utils.py
import pygame
import sys
import os
import ctypes
import json
import datetime

# 设置输入法为英文
def set_input_method_to_english():
    try:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hkl = user32.GetKeyboardLayout(0)
        if hkl != 0x0409:
            user32.LoadKeyboardLayoutW("00000409", 0x00000001)
    except:
        print("请手动调整输入法为英文输入法")

# 获取当前输入法（键盘布局句柄）
def get_current_input_method():
    try:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        return user32.GetKeyboardLayout(0)
    except:
        return None

# 恢复先前输入法
def restore_input_method(hkl):
    try:
        if hkl:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            user32.ActivateKeyboardLayout(hkl, 0)
    except:
        pass

def resource_path(relative_path):
    """ 获取资源绝对路径，兼容开发环境和PyInstaller打包环境 """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 修改 load_sound 函数
def load_sound(filename):
    try:
        # 使用新的资源路径函数
        path = resource_path(os.path.join("music", filename))
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"无法加载音效 {filename}: {str(e)}")
        class DummySound:
            def play(self): pass
        return DummySound()
    
# 游戏数据存储功能
class GameData:
    DATA_FILE = resource_path("game_data.json")
    
    @staticmethod
    def load_data():
        """加载游戏数据"""
        # 默认数据结构
        default_data = {
            "high_score": 0,
            "history": [],
            "saved_game": None
        }
        
        try:
            if os.path.exists(GameData.DATA_FILE):
                with open(GameData.DATA_FILE, 'r') as f:
                    # 加载现有数据并确保包含所有必要的键
                    data = json.load(f)
                    # 确保数据结构完整
                    for key in default_data:
                        if key not in data:
                            data[key] = default_data[key]
                    return data
            else:
                return default_data
        except:
            print("无法加载游戏数据，将使用默认数据")
            return default_data
    
    @staticmethod
    def save_data(data):
        """保存游戏数据"""
        try:
            with open(GameData.DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            print("无法保存游戏数据")
    
    @staticmethod
    def add_record(score, difficulty=None, floor=None):
        """添加新的游戏记录"""
        data = GameData.load_data()
        
        # 添加新记录（只添加一条）
        new_record = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "score": score
        }
        # 兼容新增字段：难度与层数
        if difficulty is not None:
            new_record["difficulty"] = difficulty
        if floor is not None:
            new_record["floor"] = floor
        data["history"].append(new_record)
        
        # 更新最高分
        if score > data["high_score"]:
            data["high_score"] = score
        
        # 只保留最近的20条记录
        data["history"] = data["history"][-20:]
        
        # 游戏结束时清除保存的游戏状态
        data["saved_game"] = None
        
        GameData.save_data(data)
        return data
    
    @staticmethod
    def get_high_score():
        """获取最高分"""
        data = GameData.load_data()
        return data["high_score"]
    
    @staticmethod
    def get_history():
        """获取历史记录"""
        data = GameData.load_data()
        return data["history"]
    
    @staticmethod
    def save_game_state(game_state):
        """保存游戏状态"""
        data = GameData.load_data()
        data["saved_game"] = game_state
        GameData.save_data(data)
        return True
    
    @staticmethod
    def load_game_state():
        """加载游戏状态"""
        data = GameData.load_data()
        return data.get("saved_game", None)
    
    @staticmethod
    def has_saved_game():
        """检查是否有保存的游戏"""
        data = GameData.load_data()
        return data["saved_game"] is not None
    

