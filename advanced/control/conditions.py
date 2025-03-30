#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
条件评估器 - 处理条件表达式
"""

import re
import logging
import traceback

logger = logging.getLogger('pixel_image_generator')

class ConditionEvaluator:
    """条件表达式评估器"""
    
    def __init__(self, expression_evaluator=None):
        """
        初始化条件评估器
        
        Args:
            expression_evaluator: 表达式评估器实例(可选)
        """
        self.expression_evaluator = expression_evaluator
        
    def evaluate_condition(self, condition, context):
        """
        评估条件表达式
        
        Args:
            condition: 条件表达式字符串
            context: 上下文变量字典
            
        Returns:
            布尔结果
        """
        try:
            # 替换条件中的变量
            for var_name, var_value in context.items():
                # 使用正则表达式确保只替换完整的变量名
                pattern = r'(^|[^a-zA-Z0-9_])' + re.escape(str(var_name)) + r'([^a-zA-Z0-9_]|$)'
                
                def replacer(match):
                    prefix = match.group(1)
                    suffix = match.group(2)
                    return f"{prefix}{var_value}{suffix}"
                    
                condition = re.sub(pattern, replacer, condition)
            
            # 安全地评估条件（仅支持基本比较运算符）
            # 首先净化条件表达式
            safe_condition = self.sanitize_condition(condition)
            
            # 评估净化后的表达式
            logger.debug(f"评估条件表达式: {safe_condition}")
            
            # 首先检查是否为简单的比较
            # 处理等于、不等于、大于、小于、大于等于、小于等于
            if '<=' in safe_condition:
                left, right = safe_condition.split('<=')
                left = float(left.strip())
                right = float(right.strip())
                return left <= right
            elif '>=' in safe_condition:
                left, right = safe_condition.split('>=')
                left = float(left.strip())
                right = float(right.strip())
                return left >= right
            elif '<' in safe_condition:
                left, right = safe_condition.split('<')
                left = float(left.strip())
                right = float(right.strip())
                return left < right
            elif '>' in safe_condition:
                left, right = safe_condition.split('>')
                left = float(left.strip())
                right = float(right.strip())
                return left > right
            elif '==' in safe_condition:
                left, right = safe_condition.split('==')
                left = left.strip()
                right = right.strip()
                
                # 尝试数值比较
                try:
                    left = float(left)
                    right = float(right)
                except ValueError:
                    # 字符串比较
                    pass
                    
                return left == right
            elif '!=' in safe_condition:
                left, right = safe_condition.split('!=')
                left = left.strip()
                right = right.strip()
                
                # 尝试数值比较
                try:
                    left = float(left)
                    right = float(right)
                except ValueError:
                    # 字符串比较
                    pass
                    
                return left != right
            elif 'and' in safe_condition.lower():
                # 处理与逻辑
                parts = safe_condition.lower().split('and')
                return all(self.evaluate_condition(part.strip(), context) for part in parts)
            elif 'or' in safe_condition.lower():
                # 处理或逻辑
                parts = safe_condition.lower().split('or')
                return any(self.evaluate_condition(part.strip(), context) for part in parts)
            elif 'not' in safe_condition.lower():
                # 处理非逻辑
                _, expr = safe_condition.lower().split('not', 1)
                return not self.evaluate_condition(expr.strip(), context)
            else:
                # 尝试用eval评估
                try:
                    # 构建安全上下文
                    safe_ctx = {"__builtins__": {}}
                    safe_ctx.update(context)
                    
                    # 添加比较函数
                    safe_ctx.update({
                        "eq": lambda x, y: x == y,
                        "ne": lambda x, y: x != y,
                        "lt": lambda x, y: x < y,
                        "le": lambda x, y: x <= y,
                        "gt": lambda x, y: x > y,
                        "ge": lambda x, y: x >= y,
                    })
                    
                    # 评估
                    result = eval(safe_condition, {"__builtins__": {}}, safe_ctx)
                    return bool(result)
                except Exception as e:
                    logger.warning(f"条件表达式评估错误: {safe_condition}, {str(e)}")
                    return False
            
        except Exception as e:
            logger.error(f"条件表达式评估错误: {condition}, 错误: {str(e)}")
            logger.debug(traceback.format_exc())
            return False
        
    def sanitize_condition(self, condition):
        """
        净化条件表达式，防止代码注入
        
        Args:
            condition: 条件表达式字符串
            
        Returns:
            净化后的条件表达式
        """
        # 仅允许这些字符和表达式
        allowed_patterns = [
            # 数字和浮点数
            r'\d+\.\d+', r'\d+',
            # 比较运算符
            r'==', r'!=', r'>', r'<', r'>=', r'<=',
            # 逻辑运算符
            r'and', r'or', r'not',
            # 算术运算符
            r'\+', r'-', r'\*', r'/', r'%',
            # 括号
            r'\(', r'\)',
            # 空白符
            r'\s+',
            # 变量名 (字母数字下划线)
            r'[a-zA-Z_][a-zA-Z0-9_]*'
        ]
        
        # 创建正则表达式模式
        pattern = '|'.join(allowed_patterns)
        
        # 提取所有匹配的部分
        tokens = re.findall(pattern, condition, re.IGNORECASE)
        
        # 重建表达式
        safe_condition = ''.join(tokens)
        
        # 检查是否有未被识别的部分（可能是危险代码）
        original_nospace = re.sub(r'\s+', '', condition)
        safe_nospace = re.sub(r'\s+', '', safe_condition)
        
        if original_nospace != safe_nospace:
            logger.warning(f"条件表达式包含不安全的部分: '{condition}'，已被净化为: '{safe_condition}'")
        
        return safe_condition.strip()
        
    def process_if_command(self, param_str, image_array, width, height, line_num=None, process_line_func=None, variables=None):
        """
        处理if命令（使用分号分隔条件和指令）
        
        Args:
            param_str: 命令参数字符串
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            line_num: 行号（用于日志）
            process_line_func: 处理单行指令的回调函数
            variables: 变量上下文
            
        Returns:
            (成功/失败, 图像数组, 宽度, 高度)的元组
        """
        if variables is None:
            variables = {}
            
        try:
            # 检查process_line_func是否有效
            if process_line_func is None or not callable(process_line_func):
                logger.error(f"第 {line_num} 行: 处理条件命令失败，未提供有效的处理函数")
                return False, image_array, width, height
            
            # 使用分号分隔条件和指令
            if ';' not in param_str:
                logger.warning(f"第 {line_num} 行: if语法格式错误，应使用分号分隔条件和指令")
                return False, image_array, width, height
            
            condition_str, instruction = param_str.split(';', 1)
            condition_str = condition_str.strip()
            instruction = instruction.strip()
            
            # 创建上下文
            context = {
                "width": width,
                "height": height
            }
            context.update(variables)  # 添加全局变量
            
            # 评估条件
            condition_result = self.evaluate_condition(condition_str, context)
            
            # 如果条件为真，执行指令
            if condition_result:
                logger.info(f"条件满足，执行指令: {instruction}")
                # 检查是否包含多个指令（用逗号分隔）
                if ',' in instruction and ':' in instruction:
                    # 多个指令，用逗号分隔
                    from .parser import InstructionParser
                    parser = InstructionParser()
                    return parser.process_comma_separated_instructions(instruction, image_array, width, height, line_num, process_line_func, variables)
                elif ':' in instruction:
                    # 单个指令
                    return process_line_func(instruction, image_array, width, height, line_num)
                else:
                    logger.warning(f"第 {line_num} 行: 无效的指令格式: {instruction}")
                    return False, image_array, width, height
            else:
                logger.info(f"条件不满足，跳过指令: {instruction}")
                return True, image_array, width, height
                
        except Exception as e:
            logger.warning(f"处理if命令出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False, image_array, width, height 