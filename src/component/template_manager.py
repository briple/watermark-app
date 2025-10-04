import os
import json

class TemplateManager:
    def __init__(self, template_file="watermark_templates.json"):
        self.template_file = template_file
        self.templates = self.load_templates()
    
    def load_templates(self):
        """加载模板文件"""
        if os.path.exists(self.template_file):
            try:
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载模板文件失败: {e}")
                return {}
        return {}
    
    def save_templates(self):
        """保存模板到文件"""
        try:
            with open(self.template_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板文件失败: {e}")
            return False
    
    def save_template(self, name, watermark_type, text_settings, image_settings):
        """保存模板"""
        self.templates[name] = {
            'watermark_type': watermark_type,
            'text_settings': text_settings,
            'image_settings': image_settings,
            'timestamp': os.path.getmtime(self.template_file) if os.path.exists(self.template_file) else 0
        }
        return self.save_templates()
    
    def load_template(self, name):
        """加载模板"""
        return self.templates.get(name)
    
    def delete_template(self, name):
        """删除模板"""
        if name in self.templates:
            del self.templates[name]
            return self.save_templates()
        return False
    
    def get_template_names(self):
        """获取所有模板名称"""
        return list(self.templates.keys())