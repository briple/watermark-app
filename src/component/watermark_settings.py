import os
import platform
import json

class WatermarkSettings:
    """全局水印设置类"""
    def __init__(self):
        self.watermark_type = "text"
        self.text_settings = {
            'text': "Watermark",
            'font_family': "Times New Roman",
            'font_size': 36,
            'bold': 0,
            'italic': 0,
            'color': "#FF0000",
            'opacity': 50,
            'shadow': 0,
            'stroke': 0,
            'stroke_width': 2,
            'position': "center"
        }
        self.image_settings = {
            'image_path': '',
            'scale_percent': 30,
            'opacity': 50,
            'position': "center"
        }
        self.custom_position = None  # 自定义位置 (rel_x, rel_y)
        self._version = 0  # 添加版本号用于检测设置变化
    
    def update_text_setting(self, key, value):
        """更新文本水印设置"""
        if key in self.text_settings and self.text_settings[key] != value:
            self.text_settings[key] = value
            self._version += 1  # 设置变化时增加版本号
    
    def update_image_setting(self, key, value):
        """更新图片水印设置"""
        if key in self.image_settings and self.image_settings[key] != value:
            self.image_settings[key] = value
            self._version += 1  # 设置变化时增加版本号
    
    def set_watermark_type(self, value):
        """设置水印类型"""
        if self.watermark_type != value:
            self.watermark_type = value
            self._version += 1
    
    def set_custom_position(self, value):
        """设置自定义位置"""
        if self.custom_position != value:
            self.custom_position = value
            self._version += 1

# 创建全局水印设置实例
global_watermark_settings = WatermarkSettings()