#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代码安全处理器 - 为表达式和条件提供安全过滤功能
"""

import re
import logging

logger = logging.getLogger('pixel_image_generator')

class CodeSanitizer:
    """代码安全过滤器"""
    
    @staticmethod
    def sanitize_expression(expr):
        """
        净化表达式，移除潜在的危险代码
        
        Args:
            expr: 要净化的表达式
            
        Returns:
            净化后的表达式
        """
        # 移除可能导致安全问题的函数和关键字
        dangerous_patterns = [
            r'__.*__',               # 双下划线方法
            r'eval\s*\(',            # eval函数
            r'exec\s*\(',            # exec函数
            r'compile\s*\(',         # compile函数
            r'globals\s*\(',         # globals函数
            r'locals\s*\(',          # locals函数
            r'getattr\s*\(',         # getattr函数
            r'setattr\s*\(',         # setattr函数
            r'delattr\s*\(',         # delattr函数
            r'open\s*\(',            # open函数
            r'import\s+',            # import语句
            r'from\s+.*\s+import',   # from import语句
        ]
        
        # 检查危险模式
        for pattern in dangerous_patterns:
            if re.search(pattern, expr, re.IGNORECASE):
                logger.warning(f"表达式包含潜在危险代码: {expr}")
                expr = "0"  # 返回安全值
                break
                
        return expr
        
    @staticmethod
    def sanitize_condition(condition):
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