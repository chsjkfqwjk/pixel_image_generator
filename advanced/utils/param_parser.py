#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
参数解析器 - 提供参数处理功能
"""

import re
import logging

logger = logging.getLogger('pixel_image_generator')

class ParamParser:
    """参数解析器"""
    
    def __init__(self, expression_evaluator=None, ternary_evaluator=None):
        """
        初始化参数解析器
        
        Args:
            expression_evaluator: 表达式评估器实例(可选)
            ternary_evaluator: 三元表达式评估器实例(可选)
        """
        self.expression_evaluator = expression_evaluator
        self.ternary_evaluator = ternary_evaluator
        
    def parse_params_with_backslash(self, param_str, variables=None):
        """
        使用反斜杠分隔参数，考虑引号和花括号的情况
        
        Args:
            param_str: 参数字符串
            variables: 变量上下文
            
        Returns:
            参数列表
        """
        if variables is None:
            variables = {}
            
        params = []
        current_param = ""
        i = 0
        in_quotes = False
        quote_char = None
        in_braces = 0
        
        # 逐字符处理
        while i < len(param_str):
            char = param_str[i]
            
            # 处理引号（保持引号内的内容完整）
            if char in "\"'" and (i == 0 or param_str[i-1] != "\\"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_param += char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                    current_param += char
                else:
                    current_param += char
            # 处理花括号（不拆分花括号内的内容）
            elif char == '{' and not in_quotes:
                in_braces += 1
                current_param += char
            elif char == '}' and not in_quotes:
                in_braces = max(0, in_braces - 1)  # 防止不匹配的括号
                current_param += char
            # 处理参数分隔符（反斜杠）- 但不能在引号或花括号内
            elif char == "\\" and not in_quotes and in_braces == 0:
                # 找到一个参数分隔符
                params.append(current_param.strip())
                current_param = ""
            # 正常字符
            else:
                current_param += char
            
            i += 1
        
        # 添加最后一个参数
        if current_param.strip():
            params.append(current_param.strip())
        
        # 处理花括号中的表达式
        processed_params = []
        for param in params:
            if '{' in param and '}' in param:
                # 寻找所有的花括号表达式
                pattern = r'\{([^{}]*)\}'
                matches = re.findall(pattern, param)
                processed_param = param
                
                for match in matches:
                    original = '{' + match + '}'
                    # 检查是否是三元表达式
                    if '?' in match and ':' in match and self.ternary_evaluator is not None:
                        result = self.ternary_evaluator.evaluate_ternary(match, variables)
                        if result is not None:
                            processed_param = processed_param.replace(original, str(result))
                    elif self.expression_evaluator is not None:
                        # 尝试计算普通表达式
                        try:
                            value = self.expression_evaluator.eval_expression_with_cache(match, variables)
                            if value is not None:
                                # 如果结果是整数，去掉小数点
                                if isinstance(value, float) and value == int(value):
                                    value = int(value)
                                processed_param = processed_param.replace(original, str(value))
                        except Exception as e:
                            logger.warning(f"处理参数表达式 '{match}' 失败: {str(e)}")
                            # 保持原样
                
                processed_params.append(processed_param)
            else:
                processed_params.append(param)
        
        return processed_params 