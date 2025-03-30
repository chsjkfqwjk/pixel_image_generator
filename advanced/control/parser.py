#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指令解析器 - 处理复杂指令解析
"""

import re
import logging
import traceback

logger = logging.getLogger('pixel_image_generator')

class InstructionParser:
    """指令解析器"""
    
    def __init__(self, expression_evaluator=None, variable_handler=None):
        """
        初始化指令解析器
        
        Args:
            expression_evaluator: 表达式评估器实例(可选)
            variable_handler: 变量处理器实例(可选)
        """
        self.expression_evaluator = expression_evaluator
        self.variable_handler = variable_handler
        
    def parse_instruction_list(self, instruction_text, line_num=None):
        """
        解析逗号分隔的指令列表，考虑引号和花括号嵌套
        
        Args:
            instruction_text: 包含逗号分隔的指令的文本
            line_num: 行号（用于日志）
            
        Returns:
            解析后的指令列表
        """
        instructions = []
        
        # 检查是否为多条指令
        if "," in instruction_text:
            # 分解多条指令，考虑引号内和花括号内的情况
            in_quotes = False
            quote_char = None
            in_nested = 0  # 跟踪嵌套层级
            current = ""
            
            for char in instruction_text:
                if char in "\"'" and not in_nested:
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                        current += char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                        current += char
                    else:
                        current += char
                elif char == '{' and not in_quotes:
                    in_nested += 1
                    current += char
                elif char == '}' and not in_quotes:
                    in_nested = max(0, in_nested - 1)  # 防止不平衡的括号
                    current += char
                elif char == ',' and not in_quotes and in_nested == 0:
                    # 找到分隔符（确保不在引号内和花括号内）
                    instructions.append(current.strip())
                    current = ""
                else:
                    current += char
            
            # 添加最后一部分
            if current:
                instructions.append(current.strip())
        else:
            # 单条指令
            instructions = [instruction_text.strip()]
        
        # 过滤掉空指令
        instructions = [instr for instr in instructions if instr]
            
        return instructions
        
    def process_comma_separated_instructions(self, instructions, image_array, width, height, line_num=None, process_line_func=None, variables=None):
        """
        处理逗号分隔的多条指令
        
        Args:
            instructions: 指令文本或指令列表
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
            # 分析指令结构
            result = True
            
            # 如果输入是字符串，先解析为指令列表
            if isinstance(instructions, str):
                processed_instrs = self.parse_instruction_list(instructions, line_num)
            else:
                processed_instrs = instructions
            
            # 检查process_line_func是否有效
            if process_line_func is None or not callable(process_line_func):
                logger.error(f"第 {line_num} 行: 处理多条指令失败，未提供有效的处理函数")
                return False, image_array, width, height
            
            # 准备不同类型的指令
            color_instrs = []
            region_instrs = []
            other_instrs = []
            
            # 对指令进行分类
            for instr in processed_instrs:
                if not instr:
                    continue
                    
                if instr.startswith("color:"):
                    color_instrs.append(instr)
                elif instr.startswith("region:"):
                    region_instrs.append(instr)
                else:
                    other_instrs.append(instr)
            
            # 按顺序执行：先颜色，再区域，最后其他指令
            all_ordered_instrs = color_instrs + region_instrs + other_instrs
            
            # 执行每个指令
            for i, instr in enumerate(all_ordered_instrs):
                if not instr:
                    continue
                
                if ':' not in instr:
                    logger.warning(f"第 {line_num} 行: 无效的指令格式 (缺少':'): {instr}")
                    result = False
                    continue
                    
                # 对每个指令执行process_line
                logger.debug(f"处理子指令 {i+1}/{len(all_ordered_instrs)}: {instr}")
                
                # 先替换全局变量
                if self.variable_handler is not None:
                    for var_name, var_value in variables.items():
                        # 使用变量处理器替换变量
                        instr = self.variable_handler.replace_variable_in_instruction(instr, var_name, var_value, variables)
                else:
                    # 简单替换变量（如果没有变量处理器）
                    for var_name, var_value in variables.items():
                        instr = instr.replace(str(var_name), str(var_value))
                
                sub_result, image_array, width, height = process_line_func(instr, image_array, width, height, line_num)
                
                if not sub_result:
                    logger.warning(f"第 {line_num} 行: 子指令执行失败: {instr}")
                    result = False
            
            return result, image_array, width, height
        
        except Exception as e:
            logger.error(f"处理多条指令时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False, image_array, width, height
            
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
            if '{' in param and '}' in param and self.expression_evaluator is not None:
                # 尝试计算参数中的表达式
                processed_param = self.expression_evaluator.process_expression_in_param(param, variables)
                processed_params.append(processed_param)
            else:
                processed_params.append(param)
        
        return processed_params 