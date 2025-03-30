#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
表达式计算器 - 用于计算和缓存数学表达式
"""

import re
import math
import logging
import traceback

logger = logging.getLogger('pixel_image_generator')

class ExpressionEvaluator:
    """表达式计算器，用于安全地计算表达式并缓存结果"""
    
    def __init__(self):
        """初始化表达式计算器"""
        self._expr_cache = {}
        
    def clear_expr_cache(self):
        """清除表达式计算缓存"""
        self._expr_cache.clear()
        
    def eval_expression(self, expression, variables=None):
        """
        计算表达式的值
        
        Args:
            expression: 要计算的表达式字符串
            variables: 变量上下文字典
            
        Returns:
            计算结果
        """
        if variables is None:
            variables = {}
            
        try:
            # 创建安全的执行环境
            safe_context = {"__builtins__": {}}
            
            # 添加基本数学函数
            safe_context.update({
                "abs": abs,
                "max": max,
                "min": min,
                "round": round,
                "int": int,
                "float": float,
                "pow": pow,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "floor": math.floor,
                "ceil": math.ceil,
                "pi": math.pi,
                "e": math.e
            })
            
            # 添加上下文变量
            safe_context.update(variables)
            
            # 净化表达式
            sanitized_expr = self._sanitize_expression(expression)
            
            # 计算表达式
            result = eval(sanitized_expr, {"__builtins__": {}}, safe_context)
            return result
            
        except Exception as e:
            logger.warning(f"表达式 '{expression}' 计算失败: {str(e)}")
            logger.debug(traceback.format_exc())
            return 0
            
    def eval_expression_with_cache(self, expression, variables=None):
        """
        计算表达式的值，使用缓存加速
        
        Args:
            expression: 要计算的表达式字符串
            variables: 变量上下文字典
            
        Returns:
            计算结果
        """
        if variables is None:
            variables = {}
            
        # 创建唯一缓存键
        cache_key = (expression, frozenset(variables.items()))
        
        # 如果已在缓存中，直接返回
        if cache_key in self._expr_cache:
            return self._expr_cache[cache_key]
            
        # 计算表达式
        result = self.eval_expression(expression, variables)
        
        # 缓存结果
        self._expr_cache[cache_key] = result
        
        return result
        
    def _sanitize_expression(self, expression):
        """
        净化表达式，移除潜在的危险代码
        
        Args:
            expression: 要净化的表达式字符串
            
        Returns:
            净化后的表达式
        """
        # 移除导入语句、函数调用等
        sanitized = re.sub(r'(__.*?__|import|exec|eval|compile|open|file|os|sys|subprocess)',
                           '_blocked_', expression)
        
        # 阻止使用属性访问
        sanitized = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                          '_blocked_', sanitized)
        
        return sanitized
        
    def process_expression_in_param(self, param, variables=None):
        """
        处理参数中的花括号表达式
        
        Args:
            param: 要处理的参数字符串
            variables: 变量上下文字典
            
        Returns:
            处理后的参数值
        """
        if variables is None:
            variables = {}
            
        # 如果参数不是字符串，直接返回
        if not isinstance(param, str):
            return param
            
        # 如果不包含花括号，直接返回
        if '{' not in param or '}' not in param:
            return param
            
        # 匹配花括号表达式
        pattern = r'\{([^{}]*)\}'
        
        def replace_expr(match):
            expr = match.group(1)
            try:
                # 计算表达式的值
                result = self.eval_expression_with_cache(expr, variables)
                
                # 如果结果是整数，去掉小数点
                if isinstance(result, float) and result == int(result):
                    result = int(result)
                    
                return str(result)
            except Exception as e:
                logger.warning(f"处理表达式 '{expr}' 失败: {str(e)}")
                return "{" + expr + "}"  # 保持原样
        
        # 替换所有花括号表达式
        processed_param = re.sub(pattern, replace_expr, param)
        
        return processed_param 