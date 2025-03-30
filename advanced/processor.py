#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级语法处理器 - 提供高级语法功能的主接口类
"""

import logging
import traceback
import numpy as np

from .expression.evaluator import ExpressionEvaluator
from .expression.ternary import TernaryEvaluator
from .expression.variables import VariableHandler
from .control.conditions import ConditionEvaluator
from .control.loops import LoopProcessor
from .control.parser import InstructionParser
from .utils.sanitizer import CodeSanitizer
from .utils.param_parser import ParamParser

logger = logging.getLogger('pixel_image_generator')

class AdvancedSyntaxProcessor:
    """高级语法处理器，处理条件、循环、表达式等高级功能"""
    
    def __init__(self):
        """初始化高级语法处理器"""
        # 创建表达式评估器
        self.expression_evaluator = ExpressionEvaluator()
        
        # 创建代码安全处理器
        self.code_sanitizer = CodeSanitizer()
        
        # 创建条件评估器
        self.condition_evaluator = ConditionEvaluator(self.expression_evaluator)
        
        # 创建三元表达式评估器
        self.ternary_evaluator = TernaryEvaluator(self.condition_evaluator, self.expression_evaluator)
        
        # 创建变量处理器
        self.variable_handler = VariableHandler(self.expression_evaluator, self.ternary_evaluator)
        
        # 创建参数解析器
        self.param_parser = ParamParser(self.expression_evaluator, self.ternary_evaluator)
        
        # 创建指令解析器
        self.instruction_parser = InstructionParser(self.expression_evaluator, self.variable_handler)
        
        # 创建循环处理器
        self.loop_processor = LoopProcessor(self.instruction_parser, self.expression_evaluator, self.variable_handler)
        
        # 存储变量
        self.variables = {}
        
        # 引用表达式缓存
        self._expr_cache = self.expression_evaluator._expr_cache
    
    def process_if_command(self, param_str, image_array, width, height, line_num=None, process_line_func=None):
        """
        处理if命令
        
        Args:
            param_str: 命令参数字符串
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            line_num: 行号（用于日志）
            process_line_func: 处理单行指令的回调函数
            
        Returns:
            (成功/失败, 图像数组, 宽度, 高度)的元组
        """
        return self.condition_evaluator.process_if_command(
            param_str, image_array, width, height, line_num, 
            process_line_func, self.variables
        )
    
    def process_loop_command(self, param_str, image_array, width, height, line_num=None, process_line_func=None):
        """
        处理loop命令
        
        Args:
            param_str: 命令参数字符串
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            line_num: 行号（用于日志）
            process_line_func: 处理单行指令的回调函数
            
        Returns:
            (成功/失败, 图像数组, 宽度, 高度)的元组
        """
        return self.loop_processor.process_loop_command(
            param_str, image_array, width, height, line_num,
            process_line_func, self.variables
        )
    
    def process_comma_separated_instructions(self, instructions, image_array, width, height, line_num=None, process_line_func=None):
        """
        处理逗号分隔的多条指令
        
        Args:
            instructions: 指令文本或指令列表
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            line_num: 行号（用于日志）
            process_line_func: 处理单行指令的回调函数
            
        Returns:
            (成功/失败, 图像数组, 宽度, 高度)的元组
        """
        return self.instruction_parser.process_comma_separated_instructions(
            instructions, image_array, width, height, line_num,
            process_line_func, self.variables
        )
    
    def parse_params_with_backslash(self, param_str):
        """
        使用反斜杠分隔参数
        
        Args:
            param_str: 参数字符串
            
        Returns:
            参数列表
        """
        return self.param_parser.parse_params_with_backslash(param_str, self.variables)
    
    def replace_variable_in_instruction(self, instruction, var_name, var_value):
        """
        替换指令中的变量
        
        Args:
            instruction: 要处理的指令字符串
            var_name: 变量名
            var_value: 变量值
            
        Returns:
            替换后的指令字符串
        """
        return self.variable_handler.replace_variable_in_instruction(
            instruction, var_name, var_value, self.variables
        )
    
    def evaluate_condition(self, condition, context):
        """
        评估条件表达式
        
        Args:
            condition: 条件表达式字符串
            context: 上下文变量字典
            
        Returns:
            布尔结果
        """
        return self.condition_evaluator.evaluate_condition(condition, context)
    
    def evaluate_ternary(self, ternary_expr):
        """
        评估三元表达式
        
        Args:
            ternary_expr: 三元表达式字符串
            
        Returns:
            计算结果
        """
        return self.ternary_evaluator.evaluate_ternary(ternary_expr, self.variables)
    
    def eval_expression_with_cache(self, expr, context=None):
        """
        使用缓存计算表达式的值
        
        Args:
            expr: 要计算的表达式
            context: 上下文变量
            
        Returns:
            计算结果
        """
        if context is None:
            context = self.variables.copy()
        return self.expression_evaluator.eval_expression_with_cache(expr, context)
    
    def clear_expr_cache(self):
        """清除表达式计算缓存"""
        self.expression_evaluator.clear_expr_cache()
        
    def _process_expression_in_param(self, param):
        """
        处理参数中的表达式
        
        Args:
            param: 要处理的参数
            
        Returns:
            处理后的参数
        """
        return self.expression_evaluator.process_expression_in_param(param, self.variables) 