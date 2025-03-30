#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量处理器 - 处理指令中的变量替换
"""

import re
import logging

logger = logging.getLogger('pixel_image_generator')

class VariableHandler:
    """变量处理器"""
    
    def __init__(self, expression_evaluator, ternary_evaluator=None):
        """
        初始化变量处理器
        
        Args:
            expression_evaluator: 表达式评估器实例
            ternary_evaluator: 三元表达式评估器实例(可选)
        """
        self.expression_evaluator = expression_evaluator
        self.ternary_evaluator = ternary_evaluator
        
    def replace_variable_in_instruction(self, instruction, var_name, var_value, variables=None):
        """
        替换指令中的变量（包括花括号表达式中的变量引用）
        
        Args:
            instruction: 要处理的指令字符串
            var_name: 变量名
            var_value: 变量值
            variables: 变量上下文
            
        Returns:
            替换后的指令字符串
        """
        if variables is None:
            variables = {}
            
        # 检查是否为整数值
        if isinstance(var_value, float) and var_value == int(var_value):
            var_value = int(var_value)
            
        # 替换简单的变量引用
        pattern = r'(^|[^a-zA-Z0-9_])' + re.escape(str(var_name)) + r'([^a-zA-Z0-9_]|$)'
        
        def replacer(match):
            prefix = match.group(1)
            suffix = match.group(2)
            return f"{prefix}{var_value}{suffix}"
            
        instruction = re.sub(pattern, replacer, instruction)
        
        # 替换花括号表达式中的变量，如{i*10}、{y+5}等
        pattern = r'\{([^{}]*)\}'
        
        def expr_replacer(match):
            expr = match.group(1)
            
            # 检查是否是三元表达式
            if '?' in expr and ':' in expr and self.ternary_evaluator is not None:
                try:
                    # 替换表达式中的变量
                    expr = re.sub(r'\b' + re.escape(str(var_name)) + r'\b', str(var_value), expr)
                    
                    # 创建上下文
                    context = {var_name: var_value}
                    context.update(variables)
                    
                    # 使用三元表达式评估器
                    return self.ternary_evaluator.evaluate_ternary(expr, context)
                
                except Exception as e:
                    logger.warning(f"处理三元表达式 '{expr}' 失败: {str(e)}")
                    return "{" + expr + "}"
            
            # 替换表达式中的变量
            expr = re.sub(r'\b' + re.escape(str(var_name)) + r'\b', str(var_value), expr)
            
            # 创建上下文，包含所有变量
            context = {var_name: var_value}
            context.update(variables)
            
            # 计算表达式
            try:
                # 使用表达式评估器
                calculated_value = self.expression_evaluator.eval_expression_with_cache(expr, context)
                
                # 如果结果是整数，去掉小数点
                if isinstance(calculated_value, float) and calculated_value == int(calculated_value):
                    calculated_value = int(calculated_value)
                    
                return str(calculated_value)
            except Exception as e:
                logger.warning(f"计算表达式 '{expr}' 失败: {str(e)}")
                return "{" + expr + "}"  # 保持原样
        
        # 替换所有花括号表达式
        instruction = re.sub(pattern, expr_replacer, instruction)
        
        # 处理特殊的区域命名格式 (_{变量名} 格式)
        if "_{" in instruction:
            # 1. 直接替换 _{var_name} 格式
            pattern = r"_\{" + re.escape(str(var_name)) + r"\}"
            instruction = re.sub(pattern, f"_{var_value}", instruction)
            
            # 2. 替换多个变量的情况 如 _{x}_{y}
            pattern = r"_\{([^{}]*)\}"
            
            def complex_replacer(match):
                inner_expr = match.group(1)
                # 替换表达式中的变量
                inner_expr = re.sub(r'\b' + re.escape(str(var_name)) + r'\b', str(var_value), inner_expr)
                
                # 尝试计算表达式
                try:
                    context = {var_name: var_value}
                    context.update(variables)
                    calculated = self.expression_evaluator.eval_expression_with_cache(inner_expr, context)
                    if isinstance(calculated, float) and calculated == int(calculated):
                        calculated = int(calculated)
                    return f"_{calculated}"
                except:
                    # 无法计算，保留原样
                    return f"_{{{inner_expr}}}"
                
            instruction = re.sub(pattern, complex_replacer, instruction)
            
        logger.debug(f"变量替换: '{var_name}={var_value}' 在 '{instruction}' 中")
        return instruction 