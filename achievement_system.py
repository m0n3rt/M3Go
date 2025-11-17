# achievement_system.py - 成就系统
import pygame
import json
import datetime
import os
from game_utils import resource_path

# 成就定义
ACHIEVEMENTS = {
    # 击杀相关
    "first_kill": {
        "name": "First Blood",
        "description": "Kill your first enemy",
        "type": "kill_count",
        "target": 1,
        "icon": "[!]",
        "points": 10
    },
    "killer": {
        "name": "Killer",
        "description": "Kill 50 enemies in total",
        "type": "kill_count",
        "target": 50,
        "icon": "[X]",
        "points": 50
    },
    "massacre": {
        "name": "Massacre",
        "description": "Kill 200 enemies in total",
        "type": "kill_count",
        "target": 200,
        "icon": "[*]",
        "points": 100
    },
    
    # 生存相关
    "survivor": {
        "name": "Survivor",
        "description": "Survive for more than 5 minutes",
        "type": "survival_time",
        "target": 300,  # 5分钟 = 300秒
        "icon": "[T]",
        "points": 30
    },
    "endurance": {
        "name": "Endurance",
        "description": "Survive for more than 10 minutes",
        "type": "survival_time",
        "target": 600,
        "icon": "[S]",
        "points": 80
    },
    
    # 分数相关
    "high_scorer": {
        "name": "High Scorer",
        "description": "Score 1000 points in single game",
        "type": "score",
        "target": 1000,
        "icon": "[H]",
        "points": 40
    },
    "score_master": {
        "name": "Score Master",
        "description": "Score 5000 points in single game",
        "type": "score",
        "target": 5000,
        "icon": "[M]",
        "points": 150
    },
    
    # Boss相关
    "boss_slayer": {
        "name": "Boss Slayer",
        "description": "Defeat your first Boss",
        "type": "boss_kill",
        "target": 1,
        "icon": "[B]",
        "points": 60
    },
    "boss_hunter": {
        "name": "Boss Hunter",
        "description": "Defeat 5 Bosses in total",
        "type": "boss_kill",
        "target": 5,
        "icon": "[D]",
        "points": 200
    },
    
    # 难度相关
    "risk_taker": {
        "name": "Risk Taker",
        "description": "Complete game on difficulty 10+",
        "type": "difficulty",
        "target": 10,
        "icon": "[R]",
        "points": 70
    },
    "challenger": {
        "name": "Challenger",
        "description": "Complete game on max difficulty (20)",
        "type": "difficulty",
        "target": 20,
        "icon": "[C]",
        "points": 300
    },
    
    # 层数相关
    "explorer": {
        "name": "Explorer",
        "description": "Reach floor 5",
        "type": "floor",
        "target": 5,
        "icon": "[E]",
        "points": 50
    },
    "deep_diver": {
        "name": "Deep Diver",
        "description": "Reach floor 10",
        "type": "floor",
        "target": 10,
        "icon": "[V]",
        "points": 120
    },
    "tower_master": {
        "name": "Tower Master",
        "description": "Reach the final floor (15)",
        "type": "floor",
        "target": 15,
        "icon": "[M]",
        "points": 200
    },
    "ultimate_conqueror": {
        "name": "Ultimate Conqueror",
        "description": "Complete all 15 floors successfully",
        "type": "game_complete",
        "target": 1,
        "icon": "[★]",
        "points": 500
    },
    
    # 武器相关
    "marksman": {
        "name": "Marksman",
        "description": "Kill 20 enemies with sniper rifle",
        "type": "weapon_kill",
        "target": 20,
        "weapon": 2,  # 武器索引
        "icon": "[A]",
        "points": 40
    },
    
    # 特殊成就
    "first_game": {
        "name": "Welcome Warrior",
        "description": "Start your first game",
        "type": "game_start",
        "target": 1,
        "icon": "[W]",
        "points": 5
    },
    "persistent": {
        "name": "Persistent",
        "description": "Play 10 games in total",
        "type": "game_count",
        "target": 10,
        "icon": "[P]",
        "points": 30
    }
}

class AchievementSystem:
    def __init__(self):
        self.data_file = "achievement_data.json"
        self.achievements_data = self.load_achievements()
        self.unlocked_notifications = []  # 待显示的成就通知
        
    def load_achievements(self):
        """Load achievement data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load achievement data: {e}")
        
        # Initialize default data
        return {
            "unlocked": {},  # Unlocked achievements {"achievement_id": {"date": "...", "time": "..."}}
            "progress": {},  # Achievement progress {"achievement_id": current_value}
            "stats": {       # Statistics
                "total_kills": 0,
                "total_boss_kills": 0,
                "max_survival_time": 0,
                "max_score": 0,
                "max_difficulty": 0,
                "max_floor": 0,
                "game_count": 0,
                "game_completions": 0,  # 游戏完成次数
                "weapon_kills": [0, 0, 0]  # Kills per weapon
            }
        }
    
    def save_achievements(self):
        """Save achievement data"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.achievements_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save achievement data: {e}")
    
    def update_progress(self, achievement_type, value, **kwargs):
        """Update achievement progress"""
        # 确保所有必要的字段存在
        if "game_completions" not in self.achievements_data["stats"]:
            self.achievements_data["stats"]["game_completions"] = 0
        
        stats = self.achievements_data["stats"]
        progress = self.achievements_data["progress"]
        
        # 更新统计数据
        if achievement_type == "kill_count":
            stats["total_kills"] += value
        elif achievement_type == "boss_kill":
            stats["total_boss_kills"] += value
        elif achievement_type == "survival_time":
            stats["max_survival_time"] = max(stats["max_survival_time"], value)
        elif achievement_type == "score":
            stats["max_score"] = max(stats["max_score"], value)
        elif achievement_type == "difficulty":
            stats["max_difficulty"] = max(stats["max_difficulty"], value)
        elif achievement_type == "floor":
            stats["max_floor"] = max(stats["max_floor"], value)
        elif achievement_type == "game_start" or achievement_type == "game_count":
            stats["game_count"] += 1
        elif achievement_type == "game_complete":
            stats["game_completions"] += value
        elif achievement_type == "weapon_kill":
            weapon_idx = kwargs.get("weapon", 0)
            if 0 <= weapon_idx < len(stats["weapon_kills"]):
                stats["weapon_kills"][weapon_idx] += value
        
        # 检查成就解锁
        self.check_achievements()
        self.save_achievements()
    
    def check_achievements(self):
        """Check and unlock achievements"""
        stats = self.achievements_data["stats"]
        unlocked = self.achievements_data["unlocked"]
        
        for ach_id, ach_info in ACHIEVEMENTS.items():
            if ach_id in unlocked:
                continue  # Already unlocked
                
            target_reached = False
            
            if ach_info["type"] == "kill_count":
                target_reached = stats["total_kills"] >= ach_info["target"]
            elif ach_info["type"] == "boss_kill":
                target_reached = stats["total_boss_kills"] >= ach_info["target"]
            elif ach_info["type"] == "survival_time":
                target_reached = stats["max_survival_time"] >= ach_info["target"]
            elif ach_info["type"] == "score":
                target_reached = stats["max_score"] >= ach_info["target"]
            elif ach_info["type"] == "difficulty":
                target_reached = stats["max_difficulty"] >= ach_info["target"]
            elif ach_info["type"] == "floor":
                target_reached = stats["max_floor"] >= ach_info["target"]
            elif ach_info["type"] == "game_start" or ach_info["type"] == "game_count":
                target_reached = stats["game_count"] >= ach_info["target"]
            elif ach_info["type"] == "game_complete":
                target_reached = stats["game_completions"] >= ach_info["target"]
            elif ach_info["type"] == "weapon_kill":
                weapon_idx = ach_info.get("weapon", 0)
                if 0 <= weapon_idx < len(stats["weapon_kills"]):
                    target_reached = stats["weapon_kills"][weapon_idx] >= ach_info["target"]
            
            if target_reached:
                self.unlock_achievement(ach_id)
    
    def unlock_achievement(self, achievement_id):
        """Unlock achievement"""
        if achievement_id in self.achievements_data["unlocked"]:
            return
            
        now = datetime.datetime.now()
        self.achievements_data["unlocked"][achievement_id] = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S")
        }
        
        # 添加到通知队列
        self.unlocked_notifications.append(achievement_id)
        print(f"🎉 Achievement Unlocked: {ACHIEVEMENTS[achievement_id]['name']}")
    
    def get_unlocked_achievements(self):
        """Get list of unlocked achievements"""
        return list(self.achievements_data["unlocked"].keys())
    
    def get_achievement_progress(self, achievement_id):
        """Get achievement progress"""
        if achievement_id in self.achievements_data["unlocked"]:
            return 1.0  # Completed
            
        ach_info = ACHIEVEMENTS[achievement_id]
        stats = self.achievements_data["stats"]
        
        current = 0
        if ach_info["type"] == "kill_count":
            current = stats["total_kills"]
        elif ach_info["type"] == "boss_kill":
            current = stats["total_boss_kills"]
        elif ach_info["type"] == "survival_time":
            current = stats["max_survival_time"]
        elif ach_info["type"] == "score":
            current = stats["max_score"]
        elif ach_info["type"] == "difficulty":
            current = stats["max_difficulty"]
        elif ach_info["type"] == "floor":
            current = stats["max_floor"]
        elif ach_info["type"] == "game_start" or ach_info["type"] == "game_count":
            current = stats["game_count"]
        elif ach_info["type"] == "game_complete":
            current = stats["game_completions"]
        elif ach_info["type"] == "weapon_kill":
            weapon_idx = ach_info.get("weapon", 0)
            if 0 <= weapon_idx < len(stats["weapon_kills"]):
                current = stats["weapon_kills"][weapon_idx]
        
        return min(1.0, current / ach_info["target"])
    
    def get_total_points(self):
        """Get total achievement points"""
        total = 0
        for ach_id in self.achievements_data["unlocked"]:
            if ach_id in ACHIEVEMENTS:
                total += ACHIEVEMENTS[ach_id]["points"]
        return total
    
    def get_completion_percentage(self):
        """Get completion percentage"""
        total_achievements = len(ACHIEVEMENTS)
        unlocked_count = len(self.achievements_data["unlocked"])
        return (unlocked_count / total_achievements) * 100 if total_achievements > 0 else 0
    
    def pop_notification(self):
        """Pop an achievement notification"""
        if self.unlocked_notifications:
            return self.unlocked_notifications.pop(0)
        return None
    
    def has_notifications(self):
        """Check if there are pending notifications"""
        return len(self.unlocked_notifications) > 0

# Global achievement system instance
achievement_system = AchievementSystem()
