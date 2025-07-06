import pandas as pd
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import re
from datetime import datetime
import os
import yaml

config = yaml.safe_load(open('config.yaml', 'r'))["Data Processing"]

class DataProcessor:
    def __init__(self, input_file='data.csv'):
        self.df = pd.read_csv(input_file, header=None, names=['Timestamp', 'Asset', 'Count'])
        
    def clean_zero_counts(self):
        """Remove entries where Count is 0"""
        self.df = self.df[self.df['Count'] != 0].reset_index(drop=True)
        
    def find_numeric_assets(self):
        """Find entries where Asset column contains only numbers"""
        numeric_mask = self.df['Asset'].str.match(r'^\d+$')
        return self.df[numeric_mask]
    
    def create_image_viewer(self, numeric_entries):
        """创建GUI查看数字Asset的图片并进行修正"""
        if numeric_entries.empty:
            print("没有找到数字Asset。")
            return
            
        root = tk.Tk()
        root.title("Asset校正工具")
        current_idx = 0
        
        # Convert numeric_entries to mutable list for dynamic updates
        entries_list = numeric_entries.to_dict('records')
        
        def show_image(idx):
            """显示图片和相关信息"""
            nonlocal entries_list
            if idx >= len(entries_list):
                root.destroy()
                return
                
            # 获取当前行数据
            print(idx)
            current_row = pd.Series(entries_list[idx])
            timestamp = current_row['Timestamp']
            current_asset = current_row['Asset']
            print(current_row)
            
            # 计算在同时间戳中的位置信息
            same_time_data = self.df[self.df['Timestamp'] == timestamp]
            asset_position = list(same_time_data['Asset']).index(current_asset) + 1
            total_entries = len(same_time_data)
            
            # 显示信息文本
            info_text = f"时间戳: {timestamp}\n数字Asset: {current_asset}\n"
            info_text += f"在同时间戳中位置: {asset_position}/{total_entries}"
            
            # 加载并显示图片
            try:
                img_path = os.path.join(config['images'], f"{timestamp}.png")
                img = Image.open(img_path)
                photo = ImageTk.PhotoImage(img)
                image_label.configure(image=photo)
                image_label.image = photo
                root.geometry(f"{img.width}x{img.height + 150}")
            except Exception as e:
                image_label.configure(text=f"无法加载图片: {str(e)}")
            
            info_label.configure(text=info_text)
            asset_entry.focus_set()  # Set focus to entry box
            
        def save_and_next():
            """保存修正后的Asset名称并显示下一张"""
            nonlocal current_idx, entries_list
            
            new_asset = asset_entry.get().strip()
            if new_asset:
                # 获取当前数字Asset
                old_asset = entries_list[current_idx]['Asset']
                
                # 更新主数据框
                self.df.loc[self.df['Asset'] == old_asset, 'Asset'] = new_asset
                
                # 从entries_list中移除所有相同的数字Asset
                entries_list = [entry for entry in entries_list if entry['Asset'] != old_asset]
                
                # 清空输入框并前进
                asset_entry.delete(0, tk.END)
                show_image(current_idx)
        
        # 创建GUI元素
        image_label = tk.Label(root)
        image_label.pack(pady=5)
        
        info_label = tk.Label(root, justify=tk.LEFT)
        info_label.pack(pady=5)
        
        frame = ttk.Frame(root)
        frame.pack(pady=5)
        
        ttk.Label(frame, text="输入正确的Asset名称:").pack(side=tk.LEFT)
        asset_entry = ttk.Entry(frame)
        asset_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame, text="保存并继续", command=save_and_next).pack(side=tk.LEFT)
        
        # Bind Enter key to save_and_next function
        root.bind('<Return>', lambda event: save_and_next())
        
        # 显示第一张图片
        show_image(0)
        root.mainloop()
    def save_clean_data(self):
        """Save cleaned data to CSV"""
        self.df.to_csv('data_clean.csv', index=False)

    def create_statistics(self):
        """Create statistics.csv with asset sums"""
        # Extract just the timestamp part before the underscore
        clean_timestamps = self.df['Timestamp'].str.split('_').str[0]
        
        first_time = pd.to_datetime(int(clean_timestamps.min()), unit='ms')
        last_time = pd.to_datetime(int(clean_timestamps.max()), unit='ms')
        time_elapsed = last_time - first_time
        
        asset_sums = self.df.groupby('Asset')['Count'].sum()
        
        with open('statistics.csv', 'w', encoding='utf-8') as f:
            f.write(f"First timestamp:,{first_time}\n")
            f.write(f"Last timestamp:,{last_time}\n") 
            f.write(f"Time elapsed:,{time_elapsed}\n")
            f.write("Asset,Sum\n")
            for asset, sum_value in asset_sums.items():
                f.write(f"{asset},{sum_value}\n")

def main():
    processor = DataProcessor()
    processor.clean_zero_counts()
    numeric_entries = processor.find_numeric_assets()
    processor.create_image_viewer(numeric_entries)
    processor.save_clean_data()
    processor.create_statistics()

if __name__ == "__main__":
    main()