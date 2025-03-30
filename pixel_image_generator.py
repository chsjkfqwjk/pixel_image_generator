#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
像素图像生成器
版本: 3.0.0

此程序用于解析简单的文本描述并生成像素风格的图像。
"""

import os
import sys
import re
import logging
import argparse
import numpy as np
from PIL import Image
import importlib
import traceback
import datetime
import time
import logging.handlers
# 添加colorama库用于彩色输出
import colorama
from colorama import Fore, Back, Style

# 初始化colorama
colorama.init(autoreset=True)

# 创建logs目录（如果不存在）
os.makedirs('logs', exist_ok=True)

# 获取当前时间戳
timestamp = time.strftime("%Y%m%d_%H%M%S")
log_file = f"logs/pixel_image_{timestamp}.log"

# 设置日志记录
logger = logging.getLogger('pixel_image_generator')
logger.setLevel(logging.INFO)

# 创建文件处理器，将日志输出到文件
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# 创建控制台处理器，保持控制台输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(file_format)

# 添加处理器到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 导入语法模块
from syntax.base.base import PixelSyntax

# 记录程序启动信息
logger.info(f"程序启动，日志记录到: {log_file}")

class RegionManager:
    """区域管理器，用于存储和管理定义的区域"""
    
    def __init__(self):
        self.regions = {}
        
    def add_region(self, region_id, x1, y1, x2, y2, shape="rect"):
        """添加一个区域"""
        self.regions[region_id] = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "shape": shape
        }
        
    def get_region(self, region_id):
        """获取区域信息"""
        return self.regions.get(region_id)
        
    def has_region(self, region_id):
        """检查区域是否存在"""
        return region_id in self.regions
        
    def clear(self):
        """清除所有区域"""
        self.regions.clear()

class ColorManager:
    """颜色管理器，用于存储和管理定义的颜色"""
    
    def __init__(self):
        self.colors = {}
        
    def add_color(self, color_id, r, g, b, a=255):
        """添加一个颜色"""
        self.colors[color_id] = {
            "r": r,
            "g": g,
            "b": b,
            "a": a
        }
        
    def get_color(self, color_id):
        """获取颜色信息"""
        return self.colors.get(color_id)
        
    def has_color(self, color_id):
        """检查颜色是否存在"""
        return color_id in self.colors
        
    def clear(self):
        """清除所有颜色"""
        self.colors.clear()

class SyntaxProcessor:
    """语法处理器，用于解析和执行语法指令"""
    
    def __init__(self):
        self.syntax_classes = {}
        self.region_manager = RegionManager()
        self.color_manager = ColorManager()
        self.variables = {}
        
        # 尝试导入高级语法模块
        try:
            import advanced
            self.advanced_processor = advanced.AdvancedSyntaxProcessor()
            # 同步表达式缓存引用
            self._expr_cache = self.advanced_processor._expr_cache
            logger.info("高级语法模块已加载")
        except (ImportError, ModuleNotFoundError) as e:
            self.advanced_processor = None
            # 如果高级处理器不可用，创建自己的表达式缓存
            self._expr_cache = {}
            logger.warning(f"高级语法模块导入失败: {str(e)}")
        
        self._load_syntax_classes()
        # 添加统计信息记录
        self.stats = {
            "total_lines": 0,
            "processed_lines": 0,
            "success_lines": 0,
            "failed_lines": 0,
            "failure_details": [],
            "success_details": [],
            "advanced_features_used": 0
        }
        
        # 用于跟踪嵌套循环的变量
        self._nested_loop_vars = {}
        self._last_loop_values = {}
        
    def _load_syntax_classes(self):
        """加载所有语法类"""
        # 导入基础语法
        try:
            from syntax.base import __init__
            base_module = importlib.import_module("syntax.base")
            
            if hasattr(base_module, "SYNTAX_CLASSES"):
                for syntax_class in base_module.SYNTAX_CLASSES:
                    self._register_syntax_class(syntax_class)
            else:
                logger.warning("基础语法模块未定义SYNTAX_CLASSES列表")
                
        except (ImportError, AttributeError) as e:
            logger.error(f"加载基础语法模块失败: {str(e)}")
                
    def _register_syntax_class(self, syntax_class):
        """注册语法类"""
        if issubclass(syntax_class, PixelSyntax):
            name = syntax_class.get_name()
            syntax_instance = syntax_class()
            # 设置语法实例的语法处理器引用
            if hasattr(syntax_instance, 'syntax_processor'):
                syntax_instance.syntax_processor = self
            self.syntax_classes[name] = syntax_instance
            logger.debug(f"已注册语法: {name}")
        
    def process_file(self, filepath):
        """处理一个语法文件"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"文件不存在: {filepath}")
                return None
                
            logger.info(f"正在处理文件: {filepath}")
            
            # 重置状态
            self.reset_state()
            
            # 重置统计信息
            self.stats = {
                "total_lines": 0,
                "processed_lines": 0,
                "success_lines": 0,
                "failed_lines": 0,
                "failure_details": [],
                "success_details": [],
                "advanced_features_used": 0
            }
            
            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 记录总行数
            self.stats["total_lines"] = len(lines)
            
            # 初始化图像数组和尺寸
            image_array = np.zeros((1, 1, 4), dtype=np.uint8)
            width, height = 1, 1
            
            # 逐行处理
            valid_lines = 0  # 记录有效行数（非空行和非注释行）
            for i, line in enumerate(lines, 1):
                # 跳过空行和注释行
                line = line.strip()
                if not line or line.startswith('#'):
                        continue
                        
                valid_lines += 1
                    
                # 处理行内注释
                original_line = line  # 保存原始行内容用于日志
                if '#' in line:
                    comment_pos = line.find('#')
                    # 确保 # 不在引号内
                    if not self._is_in_quotes(line, comment_pos):
                        line = line[:comment_pos].strip()
                
                # 处理语法行
                self.stats["processed_lines"] += 1
                result, image_array, width, height = self.process_line(line, image_array, width, height, i)
                
                if result:
                    self.stats["success_lines"] += 1
                    self.stats["success_details"].append(f"第 {i} 行: {original_line}")
                    logger.info(f"第 {i} 行处理成功: {original_line}")
                else:
                    self.stats["failed_lines"] += 1
                    self.stats["failure_details"].append(f"第 {i} 行: {original_line}")
                    logger.warning(f"第 {i} 行处理失败: {original_line}")
            
            # 输出统计信息
            success_rate = 0 if valid_lines == 0 else (self.stats["success_lines"] / valid_lines) * 100
            logger.info(f"文件统计: 总行数={self.stats['total_lines']}, 有效行数={valid_lines}, 成功={self.stats['success_lines']}, 失败={self.stats['failed_lines']}, 成功率={success_rate:.2f}%")
            
            # 创建PIL图像
            if width > 1 and height > 1:
                pil_image = Image.fromarray(image_array)
                return pil_image
            else:
                logger.error("未找到有效的图像配置")
                return None
        
        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
            
    def _is_in_quotes(self, text, pos):
        """检查位置是否在引号内"""
        # 简单实现，不考虑转义
        in_single_quotes = False
        in_double_quotes = False
        
        for i in range(pos):
            if text[i] == "'" and not in_double_quotes:
                in_single_quotes = not in_single_quotes
            elif text[i] == '"' and not in_single_quotes:
                in_double_quotes = not in_double_quotes
                
        return in_single_quotes or in_double_quotes
    
    def process_line(self, line, image_array, width, height, line_num=None):
        """处理一行语法"""
        try:
            # 解析指令和参数
            if ':' not in line:
                logger.warning(f"第 {line_num} 行: 无效的语法格式，缺少':'")
                return False, image_array, width, height
                
            command, param_str = line.split(':', 1)
            command = command.strip().lower()
            
            # 特殊处理if命令（使用分号分隔参数）
            if command == "if":
                # 使用高级语法处理器处理if命令
                if self.advanced_processor is not None:
                    # 同步状态到高级处理器
                    self._sync_advanced_processor()
                    # 调用高级语法处理器的if命令处理方法
                    self.stats["advanced_features_used"] += 1
                    result, image_array, width, height = self.advanced_processor.process_if_command(
                        param_str, image_array, width, height, line_num, self.process_line
                    )
                    # 从高级处理器同步变量和表达式缓存回来
                    self.variables = self.advanced_processor.variables
                    self._expr_cache = self.advanced_processor._expr_cache
                    return result, image_array, width, height
                else:
                    # 如果高级处理器不可用，直接返回失败
                    logger.error(f"第 {line_num} 行: 高级语法处理器不可用，无法处理if命令")
                    return False, image_array, width, height
            
            # 特殊处理loop命令（使用分号分隔循环头和循环体）
            if command == "loop":
                # 使用高级语法处理器处理loop命令
                if self.advanced_processor is not None:
                    # 同步状态到高级处理器
                    self._sync_advanced_processor()
                    self.stats["advanced_features_used"] += 1
                    result, image_array, width, height = self.advanced_processor.process_loop_command(
                        param_str, image_array, width, height, line_num, self.process_line
                    )
                    # 从高级处理器同步变量回来
                    self.variables = self.advanced_processor.variables
                    # 同步表达式缓存
                    self._expr_cache = self.advanced_processor._expr_cache
                    return result, image_array, width, height
                else:
                    # 如果高级处理器不可用，直接返回失败
                    logger.error(f"第 {line_num} 行: 高级语法处理器不可用，无法处理loop命令")
                    return False, image_array, width, height
            
            # 处理其他命令（统一使用反斜杠分隔参数）
            params = self._parse_params_with_backslash(param_str)
            
            # 查找对应的语法处理器
            if command not in self.syntax_classes:
                logger.warning(f"第 {line_num} 行: 未知的语法类型: {command}")
                return False, image_array, width, height
                
            syntax_handler = self.syntax_classes[command]
                
            # 解析参数
            parsed_params = syntax_handler.parse_params(params, line_num)
            if parsed_params is None:
                logger.warning(f"第 {line_num} 行: 参数解析失败 - 命令: {command}, 参数: {params}")
                return False, image_array, width, height
                
            # 应用语法
            try:
                if command == "transform":
                    result, image_array, width, height = syntax_handler.apply(
                        image_array, width, height, parsed_params
                    )
                else:
                    result, image_array, width, height = syntax_handler.apply(
                        image_array, width, height, parsed_params
                    )
                
                if not result:
                    logger.warning(f"第 {line_num} 行: 命令执行失败 - {command}")
                    
                return result, image_array, width, height
            except Exception as e:
                logger.error(f"第 {line_num} 行: 命令执行异常 - {command}: {str(e)}")
                return False, image_array, width, height
            
        except Exception as e:
            logger.error(f"处理行 {line_num} 时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False, image_array, width, height
    
    def _parse_params_with_backslash(self, param_str):
        """使用反斜杠分隔参数，考虑引号和花括号的情况"""
        # 如果高级处理器可用，使用高级处理器
        if self.advanced_processor is not None:
            # 同步状态到高级处理器
            self._sync_advanced_processor()
            params = self.advanced_processor.parse_params_with_backslash(param_str)
            # 从高级处理器同步变量和表达式缓存回来
            self.variables = self.advanced_processor.variables
            self._expr_cache = self.advanced_processor._expr_cache
            return params
        # 如果高级处理器不可用，记录错误并返回空列表
        logger.error("高级语法处理器不可用，无法解析带反斜杠的参数")
        return []
    
    def _process_comma_separated_instructions(self, instructions, image_array, width, height, line_num=None):
        """处理逗号分隔的多条指令"""
        # 使用高级语法处理器
        if self.advanced_processor is not None:
            # 同步状态到高级处理器
            self._sync_advanced_processor()
            self.stats["advanced_features_used"] += 1
            result, image_array, width, height = self.advanced_processor.process_comma_separated_instructions(
                instructions, image_array, width, height, line_num, self.process_line
            )
            # 从高级处理器同步变量和表达式缓存回来
            self.variables = self.advanced_processor.variables
            self._expr_cache = self.advanced_processor._expr_cache
            return result, image_array, width, height
        
        # 如果高级处理器不可用，记录错误并返回失败
        logger.error("高级语法处理器不可用，无法处理逗号分隔的指令")
        return False, image_array, width, height

    def _sync_advanced_processor(self):
        """同步高级处理器的状态"""
        if self.advanced_processor is not None:
            # 同步变量
            self.advanced_processor.variables = self.variables.copy()
            # 确保表达式缓存引用相同
            self._expr_cache = self.advanced_processor._expr_cache
    
    def reset_state(self):
        """重置处理器状态"""
        self.variables = {}
        self._expr_cache = {}
        self.region_manager.clear()
        self.color_manager.clear()
        
        # 重置高级处理器
        if self.advanced_processor is not None:
            self.advanced_processor.variables = {}
            self.advanced_processor._expr_cache = self._expr_cache
            self.advanced_processor.clear_expr_cache()

class PixelImageGenerator:
    """像素图像生成器主类"""
    
    def __init__(self):
        self.syntax_processor = SyntaxProcessor()
        self.file_stats = {}  # 用于存储每个文件的统计信息
        
    def _sync_advanced_processor(self):
        """同步高级处理器的状态"""
        if self.advanced_processor is not None:
            # 同步变量
            self.advanced_processor.variables = self.variables.copy()
            # 确保表达式缓存引用相同
            self._expr_cache = self.advanced_processor._expr_cache
            
    def generate_from_file(self, input_file):
        """从文件生成图像"""
        logger.info(f"开始处理文件: {input_file}")
        start_time = time.time()
        
        # 重置语法处理器的状态
        self.syntax_processor.reset_state()
            
        image = self.syntax_processor.process_file(input_file)
        
        # 保存文件处理统计信息
        self.file_stats[input_file] = self.syntax_processor.stats.copy()
        
        # 计算处理时间
        process_time = time.time() - start_time
        logger.info(f"文件处理完成，耗时: {process_time:.2f}秒")
        
        # 输出详细统计信息
        print(Fore.CYAN + "\n─── 文件处理详情 ───")
        print(Fore.WHITE + f"文件: {Fore.YELLOW}{os.path.basename(input_file)}")
        print(Fore.WHITE + f"总行数: {Fore.YELLOW}{self.file_stats[input_file]['total_lines']}")
        print(Fore.WHITE + f"处理的有效行数: {Fore.YELLOW}{self.file_stats[input_file]['processed_lines']}")
        print(Fore.WHITE + f"成功行数: {Fore.GREEN}{self.file_stats[input_file]['success_lines']}")
        print(Fore.WHITE + f"失败行数: {Fore.RED}{self.file_stats[input_file]['failed_lines']}")
        
        logger.info(f"文件统计: 总行数={self.file_stats[input_file]['total_lines']}, " 
                   f"有效行数={self.file_stats[input_file]['processed_lines']}, "
                   f"成功={self.file_stats[input_file]['success_lines']}, "
                   f"失败={self.file_stats[input_file]['failed_lines']}")
        
        if self.file_stats[input_file]['failed_lines'] > 0:
            print(Fore.YELLOW + "\n失败详情:")
            for detail in self.file_stats[input_file]['failure_details'][:5]:  # 只显示前5个错误
                print(Fore.RED + f"  ✗ {detail}")
            
            if len(self.file_stats[input_file]['failure_details']) > 5:
                print(Fore.YELLOW + f"  ... 还有 {len(self.file_stats[input_file]['failure_details']) - 5} 个错误，详见日志")
                
            logger.warning(f"失败详情: {self.file_stats[input_file]['failure_details']}")
        
        if image is not None:
            logger.info(f"图像生成成功: {input_file}")
            return image
        else:
            logger.error(f"从文件 {input_file} 生成图像失败")
            return None
            
    def generate_from_directory(self, input_dir, output_dir):
        """处理目录中的所有语法文件"""
        logger.info(f"开始批量处理目录: {input_dir}, 输出到: {output_dir}")
        start_time = time.time()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 查找所有.txt文件
        files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
        total_files = len(files)
        
        if total_files == 0:
            logger.warning(f"在目录 {input_dir} 中未找到任何.txt文件")
            print(Fore.RED + f"\n⚠️ 错误: 在目录 {input_dir} 中未找到任何.txt文件")
            return 0
            
        logger.info(f"在目录 {input_dir} 中找到 {total_files} 个.txt文件")
        print(Fore.CYAN + f"\n在目录 {Fore.YELLOW}{input_dir}{Fore.CYAN} 中找到 {Fore.GREEN}{total_files}{Fore.CYAN} 个配置文件")
        
        success_count = 0
        overall_stats = {
            "total_files": total_files,
            "success_files": 0,
            "failed_files": 0,
            "total_lines": 0,
            "processed_lines": 0,
            "success_lines": 0,
            "failed_lines": 0
        }
        
        # 绘制进度条边框
        print(Fore.CYAN + "\n┌" + "─" * 52)
        print(Fore.CYAN + "│" + " " * 50)
        print(Fore.CYAN + "└" + "─" * 50)
        
        for i, filename in enumerate(files, 1):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.txt', '.png'))
            
            # 绘制进度条
            progress_percent = i / total_files
            bar_length = int(progress_percent * 48)
            progress_bar = "█" * bar_length + "░" * (48 - bar_length)
            
            # 上移两行到进度条位置
            print(f"\033[2A", end="")
            print(Fore.CYAN + "│" + Fore.GREEN + f" {progress_bar} ")
            print(Fore.CYAN + "└" + "─" * 50)
            
            # 显示处理信息
            print(Fore.WHITE + f"正在处理: {Fore.YELLOW}{filename}{Fore.WHITE} [{i}/{total_files}]")
            logger.info(f"[{i}/{total_files}] 开始处理文件: {filename}")
            
            # 生成图像
            file_start_time = time.time()
            image = self.generate_from_file(input_path)
            file_process_time = time.time() - file_start_time
            
            # 累计统计信息
            file_stats = self.file_stats.get(input_path, {})
            overall_stats["total_lines"] += file_stats.get("total_lines", 0)
            overall_stats["processed_lines"] += file_stats.get("processed_lines", 0)
            overall_stats["success_lines"] += file_stats.get("success_lines", 0)
            overall_stats["failed_lines"] += file_stats.get("failed_lines", 0)
            
            if image is not None:
                image.save(output_path)
                print(Fore.GREEN + f"✓ 处理成功 [{Fore.YELLOW}{file_process_time:.2f}秒{Fore.GREEN}]")
                logger.info(f"[{i}/{total_files}] 文件处理成功，耗时: {file_process_time:.2f}秒, 已保存图像: {output_path}")
                success_count += 1
                overall_stats["success_files"] += 1
            else:
                print(Fore.RED + f"✗ 处理失败 [{Fore.YELLOW}{file_process_time:.2f}秒{Fore.RED}]")
                logger.error(f"[{i}/{total_files}] 文件处理失败，耗时: {file_process_time:.2f}秒: {filename}")
                overall_stats["failed_files"] += 1
            
            print() # 添加一个空行分隔
        
        # 计算总处理时间
        total_process_time = time.time() - start_time
        
        # 输出整体统计信息
        print(Fore.CYAN + "\n" + "═" * 60)
        print(Fore.YELLOW + " 📊 批量处理统计 ".center(60, "═"))
        print(Fore.CYAN + "═" * 60)
        
        success_rate = success_count/total_files*100 if total_files > 0 else 0
        success_line_rate = overall_stats['success_lines'] / overall_stats['processed_lines'] * 100 if overall_stats['processed_lines'] > 0 else 0
        
        print(Fore.WHITE + f"文件总数: {Fore.YELLOW}{total_files}{Fore.WHITE} 个")
        print(Fore.WHITE + f"处理成功: {Fore.GREEN}{success_count}{Fore.WHITE} 个")
        print(Fore.WHITE + f"处理失败: {Fore.RED}{overall_stats['failed_files']}{Fore.WHITE} 个")
        print(Fore.WHITE + f"文件成功率: {Fore.YELLOW}{success_rate:.1f}%{Fore.WHITE}")
        print(Fore.WHITE + f"指令成功率: {Fore.YELLOW}{success_line_rate:.1f}%{Fore.WHITE}")
        print(Fore.WHITE + f"总处理时间: {Fore.GREEN}{total_process_time:.2f}秒{Fore.WHITE}")
        
        logger.info(f"批量处理完成: {success_count}/{total_files} 个文件成功，"
                   f"指令成功率: {success_line_rate:.2f}%, 总处理时间: {total_process_time:.2f}秒")
        
        if success_count > 0:
            print(Fore.GREEN + f"\n✅ 生成的图像已保存到 {Fore.YELLOW}{os.path.abspath(output_dir)}{Fore.GREEN} 目录")
        
        # 生成详细报告
        self._generate_report(input_dir, output_dir, overall_stats, total_process_time)
        
        return success_count
    
    def _generate_report(self, input_dir, output_dir, overall_stats, total_process_time=0):
        """生成详细的处理报告"""
        report_path = os.path.join(output_dir, "processing_report.txt")
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("===== 像素图像生成器处理报告 =====\n\n")
                f.write(f"处理时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"输入目录: {os.path.abspath(input_dir)}\n")
                f.write(f"输出目录: {os.path.abspath(output_dir)}\n")
                f.write(f"日志文件: {log_file}\n\n")
                
                f.write("===== 整体统计 =====\n")
                f.write(f"文件总数: {overall_stats['total_files']}\n")
                f.write(f"处理成功: {overall_stats['success_files']}\n")
                f.write(f"处理失败: {overall_stats['failed_files']}\n")
                f.write(f"总行数: {overall_stats['total_lines']}\n")
                f.write(f"处理的有效行数: {overall_stats['processed_lines']}\n")
                f.write(f"成功行数: {overall_stats['success_lines']}\n")
                f.write(f"失败行数: {overall_stats['failed_lines']}\n")
                
                success_line_rate = 0 if overall_stats['processed_lines'] == 0 else (overall_stats['success_lines'] / overall_stats['processed_lines'] * 100)
                f.write(f"指令成功率: {success_line_rate:.2f}%\n")
                f.write(f"总处理时间: {total_process_time:.2f}秒\n\n")
                
                f.write("===== 详细文件统计 =====\n")
                for file_path, stats in self.file_stats.items():
                    filename = os.path.basename(file_path)
                    f.write(f"\n## 文件: {filename}\n")
                    f.write(f"总行数: {stats.get('total_lines', 0)}\n")
                    f.write(f"处理的有效行数: {stats.get('processed_lines', 0)}\n")
                    f.write(f"成功行数: {stats.get('success_lines', 0)}\n")
                    f.write(f"失败行数: {stats.get('failed_lines', 0)}\n")
                    
                    if stats.get('failed_lines', 0) > 0 and 'failure_details' in stats:
                        f.write("\n失败详情:\n")
                        for detail in stats['failure_details']:
                            f.write(f"  {detail}\n")
            
            print(f"\n详细处理报告已保存到: {report_path}")
            logger.info(f"处理报告已保存到: {report_path}")
            
        except Exception as e:
            logger.error(f"生成报告时出错: {str(e)}")
            print(f"生成报告时出错: {str(e)}")

def show_ascii_logo():
    """显示程序的ASCII艺术LOGO"""
    logo = """
    ██████╗ ██╗██╗  ██╗███████╗██╗         ██╗███╗   ███╗ █████╗  ██████╗ ███████╗    ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ 
    ██╔══██╗██║╚██╗██╔╝██╔════╝██║         ██║████╗ ████║██╔══██╗██╔════╝ ██╔════╝    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
    ██████╔╝██║ ╚███╔╝ █████╗  ██║         ██║██╔████╔██║███████║██║  ███╗█████╗      ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝
    ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║         ██║██║╚██╔╝██║██╔══██║██║   ██║██╔══╝      ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗
    ██║     ██║██╔╝ ██╗███████╗███████╗    ██║██║ ╚═╝ ██║██║  ██║╚██████╔╝███████╗    ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    """
    print(Fore.CYAN + logo)
    print(Fore.YELLOW + "═" * 150)
    print(Fore.GREEN + "像素图像生成器 v3.0.0".center(150))
    print(Fore.BLUE + "将文本配置转换为精美像素艺术".center(150))
    print(Fore.YELLOW + "═" * 150 + "\n")

def show_menu():
    """显示交互式菜单"""
    print(Fore.CYAN + "\n┌" + "─" * 42)
    print(Fore.CYAN + "│" + Fore.WHITE + " 请选择操作:".ljust(39))
    print(Fore.CYAN + "├" + "─" * 42)
    print(Fore.CYAN + "│" + Fore.YELLOW + " [1] " + Fore.WHITE + "处理input目录中的所有文件".ljust(32))
    print(Fore.CYAN + "│" + Fore.YELLOW + " [2] " + Fore.WHITE + "查看帮助信息".ljust(32))
    print(Fore.CYAN + "│" + Fore.YELLOW + " [3] " + Fore.WHITE + "语法详解与示例".ljust(32))
    print(Fore.CYAN + "│" + Fore.YELLOW + " [4] " + Fore.WHITE + "退出程序".ljust(32))
    print(Fore.CYAN + "└" + "─" * 40 + "\n")
    
    choice = input(Fore.GREEN + "请输入选项 [1-4]: " + Fore.WHITE)
    return choice

def show_processing_animation(text="处理中", duration=3):
    """显示处理动画"""
    animation = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    start_time = time.time()
    i = 0
    while time.time() - start_time < duration:
        print(Fore.CYAN + f"\r{text} {animation[i % len(animation)]}", end="")
        time.sleep(0.1)
        i += 1
    print()

def process_all_files():
    """处理所有文件的封装函数"""
    # 确保input和output目录存在
    input_dir = "input"
    output_dir = "output"
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        logger.warning(f"创建了input目录: {os.path.abspath(input_dir)}")
        print(Fore.YELLOW + f"创建了input目录: {os.path.abspath(input_dir)}")
        print(Fore.YELLOW + f"请将要处理的.txt文件放入此目录")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"创建了output目录: {os.path.abspath(output_dir)}")
    
    # 检查input目录中是否有.txt文件
    if not os.path.isdir(input_dir):
        logger.error(f"input目录不存在: {input_dir}")
        print(Fore.RED + f"错误: input目录不存在，请创建该目录并放入配置文件")
        return
    
    # 显示处理动画
    show_processing_animation("正在初始化", 1)
    
    # 执行批处理
    print(Fore.CYAN + "\n✨ 像素图像生成器 - 自动处理模式 ✨")
    print(Fore.WHITE + f"开始处理{Fore.YELLOW}input{Fore.WHITE}目录中的所有.txt文件...")
    print(Fore.WHITE + f"输出将保存到{Fore.YELLOW}output{Fore.WHITE}目录\n")
    
    generator = PixelImageGenerator()
    success_count = generator.generate_from_directory(input_dir, output_dir)
    
    if success_count > 0:
        print(Fore.GREEN + f"\n✅ 处理完成! 成功生成了 {Fore.YELLOW}{success_count}{Fore.GREEN} 个图像文件。")
    else:
        print(Fore.RED + "\n⚠️ 处理完成，但没有成功生成任何图像。")
        print(Fore.YELLOW + "请检查input目录中的文件格式是否正确。")
    
    logger.info("程序执行完毕")

def show_help():
    """显示帮助信息"""
    print(Fore.CYAN + "\n┌" + "─" * 62)
    print(Fore.CYAN + "│" + Fore.WHITE + " 像素图像生成器使用帮助 ".center(59))
    print(Fore.CYAN + "├" + "─" * 62)
    print(Fore.CYAN + "│" + Fore.WHITE + " 1. 将配置文件(.txt)放入input目录".ljust(59))
    print(Fore.CYAN + "│" + Fore.WHITE + " 2. 选择菜单中的'处理input目录中的所有文件'选项".ljust(59))
    print(Fore.CYAN + "│" + Fore.WHITE + " 3. 生成的图像将保存在output目录中".ljust(59))
    print(Fore.CYAN + "│" + "".ljust(59))
    print(Fore.CYAN + "│" + Fore.YELLOW + " 文件格式说明:".ljust(59))
    print(Fore.CYAN + "│" + Fore.WHITE + " - 每行使用'命令:参数'格式".ljust(59))
    print(Fore.CYAN + "│" + Fore.WHITE + " - 参数之间使用反斜杠(\\)分隔".ljust(59))
    print(Fore.CYAN + "│" + Fore.WHITE + " - 可以使用#添加注释".ljust(59))
    print(Fore.CYAN + "│" + "".ljust(59))
    print(Fore.CYAN + "│" + Fore.YELLOW + " 更多详细信息请参考文档。".ljust(59))
    print(Fore.CYAN + "└" + "─" * 60 + "\n")
    
    input(Fore.GREEN + "按回车键返回主菜单..." + Fore.WHITE)

def show_syntax_examples():
    """显示语法详解并提供示例导出功能"""
    while True:
        print(Fore.CYAN + "\n┌" + "─" * 62)
        print(Fore.CYAN + "│" + Fore.WHITE + " 语法详解与示例".center(59))
        print(Fore.CYAN + "├" + "─" * 62)
        print(Fore.CYAN + "│" + Fore.YELLOW + " [1] " + Fore.WHITE + "查看基础语法".ljust(57))
        print(Fore.CYAN + "│" + Fore.YELLOW + " [2] " + Fore.WHITE + "查看高级语法".ljust(57))
        print(Fore.CYAN + "│" + Fore.YELLOW + " [3] " + Fore.WHITE + "导出基础示例文件".ljust(57))
        print(Fore.CYAN + "│" + Fore.YELLOW + " [4] " + Fore.WHITE + "导出高级示例文件".ljust(57))
        print(Fore.CYAN + "│" + Fore.YELLOW + " [5] " + Fore.WHITE + "返回主菜单".ljust(57))
        print(Fore.CYAN + "└" + "─" * 60 + "\n")
        
        choice = input(Fore.GREEN + "请输入选项 [1-5]: " + Fore.WHITE)
        
        if choice == '1':
            show_basic_syntax()
        elif choice == '2':
            show_advanced_syntax()
        elif choice == '3':
            export_basic_example()
        elif choice == '4':
            export_advanced_example()
        elif choice == '5':
            break
        else:
            print(Fore.RED + "无效的选择，请重新输入！")
            time.sleep(1)

def show_basic_syntax():
    """显示基础语法详解（带分页功能）"""
    basic_syntax_pages = [
        # 第1页 - 基本配置
        [
            (Fore.YELLOW + " config: " + Fore.WHITE + "配置图像尺寸和背景颜色", 
             [" 格式: config:宽度\\高度\\背景红\\背景绿\\背景蓝",
              " 例如: config:800\\600\\240\\240\\240", 
              " 作用: 必须在文件开头设置，定义画布大小和背景颜色",
              " 参数: 宽度和高度为像素单位; RGB值范围为0-255"]),
              
            (Fore.YELLOW + " color: " + Fore.WHITE + "定义颜色",
             [" 格式: color:颜色ID\\红\\绿\\蓝[\\透明度]",
              " 例如: color:blue\\0\\0\\255  color:semi_red\\255\\0\\0\\128",
              " 作用: 定义可重用的颜色，透明度可选(0-255，0为完全透明)",
              " 说明: 颜色ID可在后续命令中引用，如fill:box\\blue"])
        ],
        
        # 第2页 - 区域与填充
        [
            (Fore.YELLOW + " region: " + Fore.WHITE + "定义区域",
             [" 格式: region:区域ID\\x1|y1\\x2|y2[\\形状]",
              " 例如: region:box\\10|10\\100|100  region:circ\\10|10\\100|100\\ellipse",
              " 形状参数: rect(默认), ellipse, triangle, star",
              " 作用: 定义可操作的区域，用于后续的填充、变换等操作"]),
              
            (Fore.YELLOW + " fill: " + Fore.WHITE + "填充区域",
             [" 格式: fill:区域ID\\颜色ID",
              " 例如: fill:box\\blue  fill:circ\\red",
              " 作用: 用预定义的颜色填充已定义的区域",
              " 说明: 只能使用先前通过color命令定义的颜色ID"])
        ],
        
        # 第3页 - 渐变与图案
        [
            (Fore.YELLOW + " gradient: " + Fore.WHITE + "渐变填充",
             [" 格式: gradient:区域ID\\类型\\起点x|y\\终点x|y\\起始颜色\\结束颜色",
              " 例如: gradient:box\\linear\\0|0\\100|100\\red\\blue",
              " 类型: linear(线性渐变), radial(径向渐变)",
              " 作用: 创建从一种颜色到另一种颜色的平滑过渡效果"]),
              
            (Fore.YELLOW + " points: " + Fore.WHITE + "点阵填充", 
             [" 格式: points:区域ID\\颜色\\模式\\密度\\点大小",
              " 例如: points:box\\red\\random\\0.5\\2",
              " 模式: random(随机分布), grid(网格分布), wave(波浪分布)",
              " 作用: 在区域内创建点阵图案，密度范围0.0-1.0"])
        ],
        
        # 第4页 - 路径与变换
        [
            (Fore.YELLOW + " path: " + Fore.WHITE + "绘制路径",
             [" 格式: path:点1x|y-点2x|y-...-点nx|y\\颜色\\线宽[\\样式]",
              " 例如: path:10|10-100|10-100|100-10|100-10|10\\blue\\2",
              " 样式: solid(默认), dashed, dotted",
              " 作用: 绘制连接多个点的路径线条"]),
              
            (Fore.YELLOW + " transform: " + Fore.WHITE + "变换区域",
             [" 格式: transform:区域ID\\变换类型\\参数",
              " 例如: transform:box\\rotate\\45  transform:circ\\scale\\1.5",
              " 变换类型: rotate(旋转), scale(缩放), translate(平移), flip(翻转)",
              " 作用: 对已定义的区域应用几何变换"])
        ],
        
        # 第5页 - 混合模式与变量
        [
            (Fore.YELLOW + " blend: " + Fore.WHITE + "图层混合模式",
             [" 格式: blend:区域ID\\混合模式",
              " 例如: blend:box\\overlay  blend:circ\\multiply",
              " 混合模式: normal, multiply, screen, overlay, dodge, burn",
              " 作用: 设置区域与下方图层的混合方式"]),
              
            (Fore.YELLOW + " var: " + Fore.WHITE + "定义变量",
             [" 格式: var:变量名\\值",
              " 例如: var:radius\\50  var:center_x\\{width/2}",
              " 作用: 定义可在后续表达式中使用的变量",
              " 说明: 值可以是数字、字符串或表达式(用{}包围)"])
        ]
    ]
    
    current_page = 0
    total_pages = len(basic_syntax_pages)
    
    while True:
        # 清屏（仅支持部分终端）
        print("\n" * 3)
        
        # 显示页面标题和分页信息
        print(Fore.CYAN + "┌" + "─" * 62)
        print(Fore.CYAN + "│" + Fore.WHITE + f" 基础语法详解 ({current_page+1}/{total_pages})".center(59))
        print(Fore.CYAN + "├" + "─" * 62)
        
        # 显示当前页内容
        for section in basic_syntax_pages[current_page]:
            header, details = section
            print(Fore.CYAN + "│" + header.ljust(59 - len(header) + len(Fore.YELLOW) + len(Fore.WHITE)))
            for line in details:
                print(Fore.CYAN + "│" + Fore.WHITE + line.ljust(59))
            print(Fore.CYAN + "│" + " ".ljust(59))
        
        # 显示导航信息
        print(Fore.CYAN + "├" + "─" * 62)
        nav_text = " [p]上一页 | [n]下一页 | [q]返回"
        print(Fore.CYAN + "│" + Fore.GREEN + nav_text.center(59))
        print(Fore.CYAN + "└" + "─" * 60 + "\n")
        
        # 获取用户输入
        choice = input(Fore.GREEN + "请选择操作 [p/n/q]: " + Fore.WHITE)
        
        if choice.lower() == 'p':
            # 上一页
            current_page = (current_page - 1) % total_pages
        elif choice.lower() == 'n':
            # 下一页
            current_page = (current_page + 1) % total_pages
        elif choice.lower() == 'q':
            # 退出
            break
        else:
            print(Fore.RED + "无效的选择，请重新输入！")
            time.sleep(0.5)

def show_advanced_syntax():
    """显示高级语法详解（带分页功能）"""
    advanced_syntax_pages = [
        # 第1页 - 条件与循环
        [
            (Fore.YELLOW + " if: " + Fore.WHITE + "条件判断",
             [" 格式: if:条件表达式;指令1,指令2,...",
              " 例如: if:width>600;fill:box\\blue,color:highlight\\255\\0\\0",
              " 作用: 根据条件表达式执行一组指令",
              " 说明: 多条指令用逗号分隔，条件和指令用分号分隔"]),
              
            (Fore.YELLOW + " loop: " + Fore.WHITE + "循环语法",
             [" 格式: loop:变量\\起始值\\结束值\\步长;指令1,指令2,...",
              " 例如: loop:i\\0\\4\\1;region:r{i}\\{i*50}|0\\{i*50+40}|40",
              " 作用: 重复执行一组指令，可在指令中使用循环变量",
              " 说明: 循环头和循环体用分号分隔，循环体中多条指令用逗号分隔"])
        ],
        
        # 第2页 - 表达式与变量
        [
            (Fore.YELLOW + " 表达式: " + Fore.WHITE + "动态计算值",
             [" 格式: {数学表达式或逻辑表达式}",
              " 例如: {width/2} {x+y*10} {i%2==0?100:200}",
              " 支持运算: +, -, *, /, %, **, <, >, <=, >=, ==, !=, &&, ||",
              " 说明: 表达式可以在几乎任何参数位置使用"]),
              
            (Fore.YELLOW + " 三元表达式: " + Fore.WHITE + "条件选择",
             [" 格式: {条件?真值:假值}",
              " 例如: {x>100?red:blue} {i%2==0?'偶数':'奇数'}",
              " 作用: 根据条件选择不同的值",
              " 说明: 可嵌套使用，如{x>100?{y>50?red:green}:blue}"])
        ],
        
        # 第3页 - 嵌套语法与高级技巧
        [
            (Fore.YELLOW + " 嵌套循环: " + Fore.WHITE + "多维迭代",
             [" 格式: loop:外层变量\\..;loop:内层变量\\..;指令",
              " 例如: loop:x\\0\\3\\1;loop:y\\0\\3\\1;fill:cell_{x}_{y}\\...",
              " 作用: 创建网格或复杂模式",
              " 说明: 嵌套层数没有理论限制，但建议不超过3层"]),
              
            (Fore.YELLOW + " 变量作用域: " + Fore.WHITE + "变量的可见范围",
             [" 全局变量: 在主配置中定义，所有地方可见",
              " 循环变量: 在循环内部和嵌套的循环中可见",
              " 内置变量: width, height, center_x, center_y等",
              " 作用: 理解变量可见性，避免命名冲突"])
        ],
        
        # 第4页 - 函数与宏
        [
            (Fore.YELLOW + " 内置函数: " + Fore.WHITE + "用于表达式计算",
             [" 数学函数: sin(), cos(), tan(), sqrt(), abs(), pow(), round()",
              " 例如: {sin(i*0.1)*100} {sqrt(x*x+y*y)}",
              " 随机函数: rand(), randint(min,max)",
              " 字符串函数: concat(), format()"]),
              
            (Fore.YELLOW + " 宏定义: " + Fore.WHITE + "代码复用",
             [" 格式: 用变量存储复杂表达式以便复用",
              " 例如: var:draw_circle\\fill:c{i}\\{center_x}|..|{radius}...",
              " 使用: macro:{draw_circle}",
              " 说明: 高级功能，需要配合特定语法使用"])
        ],
        
        # 第5页 - 性能优化与调试
        [
            (Fore.YELLOW + " 性能优化: " + Fore.WHITE + "提高解析和渲染速度",
             [" 表达式缓存: 相同的表达式只计算一次",
              " 例如: 使用变量存储复杂计算结果",
              " 批量操作: 一次循环中处理多个元素", 
              " 区域合并: 相邻相同颜色的区域自动合并"]),
              
            (Fore.YELLOW + " 调试技巧: " + Fore.WHITE + "排查语法问题",
             [" 注释: 使用#注释掉复杂部分，逐步排查问题", 
              " 变量检查: 打印变量值 debug:var_name",
              " 区域可视化: debug:region:区域ID",
              " 错误日志: 查看日志文件了解详细错误信息"])
        ]
    ]
    
    current_page = 0
    total_pages = len(advanced_syntax_pages)
    
    while True:
        # 清屏（仅支持部分终端）
        print("\n" * 3)
        
        # 显示页面标题和分页信息
        print(Fore.CYAN + "┌" + "─" * 62)
        print(Fore.CYAN + "│" + Fore.WHITE + f" 高级语法详解 ({current_page+1}/{total_pages})".center(59))
        print(Fore.CYAN + "├" + "─" * 62)
        
        # 显示当前页内容
        for section in advanced_syntax_pages[current_page]:
            header, details = section
            print(Fore.CYAN + "│" + header.ljust(59 - len(header) + len(Fore.YELLOW) + len(Fore.WHITE)))
            for line in details:
                print(Fore.CYAN + "│" + Fore.WHITE + line.ljust(59))
            print(Fore.CYAN + "│" + " ".ljust(59))
        
        # 显示导航信息
        print(Fore.CYAN + "├" + "─" * 62)
        nav_text = " [p]上一页 | [n]下一页 | [q]返回"
        print(Fore.CYAN + "│" + Fore.GREEN + nav_text.center(59))
        print(Fore.CYAN + "└" + "─" * 60 + "\n")
        
        # 获取用户输入
        choice = input(Fore.GREEN + "请选择操作 [p/n/q]: " + Fore.WHITE)
        
        if choice.lower() == 'p':
            # 上一页
            current_page = (current_page - 1) % total_pages
        elif choice.lower() == 'n':
            # 下一页
            current_page = (current_page + 1) % total_pages
        elif choice.lower() == 'q':
            # 退出
            break
        else:
            print(Fore.RED + "无效的选择，请重新输入！")
            time.sleep(0.5)

def export_basic_example():
    """导出基础语法示例文件"""
    example_path = "input/basic_example.txt"
    
    basic_example = """# 像素图像生成器基础语法示例文件
# 这是一个注释行，不会被执行

# 配置图像尺寸和背景色（白色背景）
config:400\\300\\255\\255\\255

# 定义几个颜色
color:blue\\0\\0\\255       # 蓝色
color:red\\255\\0\\0        # 红色
color:green\\0\\255\\0      # 绿色
color:yellow\\255\\255\\0   # 黄色
color:semi_blue\\0\\0\\255\\128  # 半透明蓝色
color:dark_blue\\0\\0\\128  # 深蓝色

# 定义几个区域
region:box1\\50|50\\150|150           # 矩形区域
region:circle\\200|50\\300|150\\ellipse  # 椭圆区域
region:tri\\50|170\\150|270\\triangle    # 三角形区域
region:star\\200|170\\300|270\\star      # 五角星区域

# 填充这些区域（只能使用预定义的颜色）
fill:box1\\red      # 用红色填充第一个矩形
fill:circle\\blue   # 用蓝色填充椭圆
fill:tri\\green     # 用绿色填充三角形
fill:star\\yellow   # 用黄色填充五角星

# 使用渐变填充
region:gradient_box\\20|20\\380|40
gradient:gradient_box\\linear\\20|20\\380|40\\red\\blue  # 线性渐变，从红色到蓝色

# 使用点阵图案
region:dots\\20|60\\380|80
points:dots\\green\\random\\0.5\\2  # 随机绿点，50%密度，2像素大小

# 绘制路径
path:20|100-380|100-380|120-20|120-20|100\\blue\\2  # 蓝色矩形轮廓
path:20|140-380|140\\red\\3\\dashed  # 红色虚线

# 变换操作
region:rotate_box\\200|200\\300|240
fill:rotate_box\\dark_blue
transform:rotate_box\\rotate\\45  # 旋转45度
"""
    
    # 替换多余的反斜杠，解决转义问题
    basic_example = basic_example.replace("\\\\", "\\")
    
    # 确保input目录存在
    os.makedirs("input", exist_ok=True)
    
    # 写入示例文件
    with open(example_path, "w", encoding="utf-8") as f:
        f.write(basic_example)
    
    print(Fore.GREEN + f"\n✓ 基础语法示例文件已导出到: {os.path.abspath(example_path)}")
    input(Fore.GREEN + "\n按回车键继续..." + Fore.WHITE)

def export_advanced_example():
    """导出高级语法示例文件"""
    example_path = "input/advanced_example.txt"
    
    advanced_example = """# 像素图像生成器高级语法示例文件
# 这是一个注释行，不会被执行

# 配置图像尺寸和背景色（浅灰色背景）
config:600\\400\\240\\240\\240

# 定义变量
var:center_x\\{600/2}  # 中心x坐标
var:center_y\\{400/2}  # 中心y坐标
var:box_size\\50       # 盒子大小

# 定义颜色
color:highlight\\255\\0\\0    # 高亮色（红色）
color:normal\\0\\0\\255       # 普通色（蓝色）
color:alt1\\0\\255\\0         # 绿色
color:alt2\\255\\255\\0       # 黄色

# 使用条件语句
if:center_x > 250;color:highlight_alt\\255\\100\\100,color:normal_alt\\100\\100\\255  # 根据条件定义不同颜色

# 创建一个中心区域
region:center\\{center_x-box_size}|{center_y-box_size}\\{center_x+box_size}|{center_y+box_size}
fill:center\\highlight  # 填充中心区域

# 使用循环创建多个方块和颜色
loop:i\\0\\9\\1;color:c{i}\\{i*25}\\100\\{255-i*20},region:r{i}\\{i*60}|20\\{i*60+50}|70,fill:r{i}\\c{i}

# 使用嵌套循环创建网格
loop:x\\0\\4\\1;loop:y\\0\\4\\1;region:grid_{x}_{y}\\{x*100+150}|{y*60+100}\\{x*100+190}|{y*60+140},fill:grid_{x}_{y}\\{(x+y)%2==0?highlight:normal}

# 三元表达式和条件填充
region:bottom\\0|320\\600|380
fill:bottom\\{center_x<300?highlight:normal}  # 根据条件选择颜色

# 创建同心圆
loop:r\\10\\100\\15;region:ring_{r}\\{center_x-r}|{center_y-r}\\{center_x+r}|{center_y+r}\\ellipse,fill:ring_{r}\\{r%30==0?highlight:normal}

# 使用表达式绘制路径
path:{center_x-100}|{center_y+150}-{center_x}|{center_y+100}-{center_x+100}|{center_y+150}\\highlight\\3  # 高亮色路径
"""
    
    # 替换多余的反斜杠，解决转义问题
    advanced_example = advanced_example.replace("\\\\", "\\")
    
    # 确保input目录存在
    os.makedirs("input", exist_ok=True)
    
    # 写入示例文件
    with open(example_path, "w", encoding="utf-8") as f:
        f.write(advanced_example)
    
    print(Fore.GREEN + f"\n✓ 高级语法示例文件已导出到: {os.path.abspath(example_path)}")
    input(Fore.GREEN + "\n按回车键继续..." + Fore.WHITE)

# 主函数
def main():
    """程序主函数"""
    show_ascii_logo()
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            process_all_files()
            input(Fore.GREEN + "\n按回车键返回主菜单..." + Fore.WHITE)
        elif choice == '2':
            show_help()
        elif choice == '3':
            show_syntax_examples()
        elif choice == '4':
            print(Fore.YELLOW + "\n感谢使用像素图像生成器！再见👋\n")
            break
        else:
            print(Fore.RED + "无效的选择，请重新输入！")
            time.sleep(1)

# 直接运行时的入口点
if __name__ == "__main__":
    main()