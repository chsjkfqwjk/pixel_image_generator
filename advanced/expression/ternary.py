#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
三元表达式计算器 - 用于处理三元表达式 (条件?值1:值2)
"""

import logging
import traceback
import re

logger = logging.getLogger('pixel_image_generator')

class TernaryEvaluator:
    """三元表达式评估器"""
    
    def __init__(self, condition_evaluator, expression_evaluator):
        """
        初始化三元表达式评估器
        
        Args:
            condition_evaluator: 条件评估器实例
            expression_evaluator: 表达式评估器实例
        """
        self.condition_evaluator = condition_evaluator
        self.expression_evaluator = expression_evaluator
        
    def evaluate_ternary(self, ternary_expr, variables=None):
        """
        评估三元表达式，返回结果，支持多层嵌套
        
        Args:
            ternary_expr: 三元表达式字符串 (条件?值1:值2)
            variables: 变量上下文
            
        Returns:
            计算结果
        """
        if variables is None:
            variables = {}
            
        try:
            # 检查是否是三元表达式
            if '?' not in ternary_expr or ':' not in ternary_expr:
                return ternary_expr
                
            # 简单判断是否是颜色ID而不是嵌套表达式
            if '{' not in ternary_expr and '}' not in ternary_expr and '?' not in ternary_expr[ternary_expr.index('?')+1:]:
                # 简单的三元表达式，如 "x>5?red:blue"
                return self._evaluate_simple_ternary(ternary_expr, variables)
                
            # 复杂嵌套三元表达式处理
            return self._evaluate_complex_ternary(ternary_expr, variables)
                
        except Exception as e:
            logger.warning(f"处理三元表达式 '{ternary_expr}' 失败: {str(e)}")
            logger.debug(traceback.format_exc())
            return ternary_expr  # 出错时返回原始表达式
    
    def _evaluate_simple_ternary(self, ternary_expr, variables):
        """
        处理简单三元表达式 (不包含嵌套)
        
        Args:
            ternary_expr: 简单三元表达式字符串
            variables: 变量上下文
            
        Returns:
            计算结果
        """
        # 解析三元表达式：condition?value_if_true:value_if_false
        condition_part, rest = ternary_expr.split('?', 1)
        true_part, false_part = rest.split(':', 1)
        
        condition_part = condition_part.strip()
        true_part = true_part.strip()
        false_part = false_part.strip()
        
        # 为表达式创建上下文
        context = variables.copy()
        
        # 评估条件
        condition_result = self.condition_evaluator.evaluate_condition(condition_part, context)
        
        # 根据条件结果返回true_part或false_part
        return true_part if condition_result else false_part
        
    def _evaluate_complex_ternary(self, ternary_expr, variables):
        """
        处理复杂嵌套三元表达式
        
        Args:
            ternary_expr: 复杂嵌套三元表达式字符串
            variables: 变量上下文
            
        Returns:
            计算结果
        """
        # 首先查找最外层的三元运算符
        # 这需要考虑嵌套，所以简单的split不适用
        level = 0
        question_pos = -1
        
        # 查找主问号位置（第一层嵌套）
        for i, char in enumerate(ternary_expr):
            if char == '{':
                level += 1
            elif char == '}':
                level -= 1
            elif char == '?' and level == 0:
                question_pos = i
                break
                
        if question_pos == -1:
            # 未找到问号，可能不是三元表达式
            return ternary_expr
            
        # 找到对应的冒号
        level = 0
        colon_pos = -1
        
        for i in range(question_pos + 1, len(ternary_expr)):
            char = ternary_expr[i]
            if char == '{':
                level += 1
            elif char == '}':
                level -= 1
            elif char == ':' and level == 0:
                colon_pos = i
                break
                
        if colon_pos == -1:
            # 未找到对应冒号，格式无效
            logger.warning(f"三元表达式格式无效，缺少冒号: {ternary_expr}")
            return ternary_expr
            
        # 提取三个部分
        condition_part = ternary_expr[:question_pos].strip()
        true_part = ternary_expr[question_pos+1:colon_pos].strip()
        false_part = ternary_expr[colon_pos+1:].strip()
        
        # 为表达式创建上下文
        context = variables.copy()
        
        # 评估条件
        condition_result = self.condition_evaluator.evaluate_condition(condition_part, context)
        
        # 确定要处理的分支
        result = true_part if condition_result else false_part
        
        # 递归处理可能嵌套的结果
        if '?' in result and ':' in result:
            return self.evaluate_ternary(result, variables)
            
        # 处理表达式中的变量引用
        if '{' in result and '}' in result:
            # 使用表达式计算器处理结果中的表达式
            result = self.expression_evaluator.process_expression_in_param(result, variables)
            
        return result 