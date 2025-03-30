#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
循环处理器 - 处理循环语句
"""

import numpy as np
import logging
import traceback

logger = logging.getLogger('pixel_image_generator')

class LoopProcessor:
    """循环处理器"""
    
    def __init__(self, parser=None, expression_evaluator=None, variable_handler=None):
        """
        初始化循环处理器
        
        Args:
            parser: 指令解析器实例
            expression_evaluator: 表达式评估器实例
            variable_handler: 变量处理器实例
        """
        self.parser = parser
        self.expression_evaluator = expression_evaluator
        self.variable_handler = variable_handler
        
    def process_loop_iterations(self, var, start, end, step, instructions, image_array, width, height, line_num=None, process_line_func=None, instruction_type="", variables=None):
        """
        执行循环的所有迭代
        
        Args:
            var: 循环变量名
            start: 起始值
            end: 结束值
            step: 步长
            instructions: 要执行的指令列表
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            line_num: 行号
            process_line_func: 处理单行指令的回调函数
            instruction_type: 指令类型描述
            variables: 变量上下文
            
        Returns:
            (成功标志, 更新后的图像数组, 更新后的宽度, 更新后的高度)
        """
        if not instructions:
            return True, image_array, width, height
            
        if variables is None:
            variables = {}
            
        logger.info(f"执行{instruction_type}指令（{len(instructions)}个指令）")
        
        current = start
        success = True
        
        # 计算迭代次数，防止无限循环
        max_iterations = abs(int((end - start) / step)) + 1
        if max_iterations > 1000:  # 设置合理的最大循环次数
            logger.warning(f"循环次数过多 ({max_iterations})，已限制为1000次")
            max_iterations = 1000
            
        iteration_count = 0
        
        while ((step > 0 and current <= end) or (step < 0 and current >= end)) and iteration_count < max_iterations:
            # 更新循环变量
            loop_variables = variables.copy()
            loop_variables[var] = current
            
            # 执行当前迭代的指令
            for idx, instruction in enumerate(instructions, 1):
                # 替换变量
                if self.variable_handler:
                    current_instruction = self.variable_handler.replace_variable_in_instruction(
                        instruction, var, current, loop_variables
                    )
                else:
                    # 简单替换变量（如果没有变量处理器）
                    current_instruction = instruction.replace(str(var), str(current))
                
                # 执行指令
                logger.debug(f"循环变量 {var} = {current}, 处理{instruction_type}指令: {current_instruction}")
                result, image_array, width, height = process_line_func(current_instruction, image_array, width, height, line_num)
                
                if not result:
                    logger.warning(f"循环内{instruction_type}指令执行失败: {current_instruction}")
                    success = False
            
            # 更新循环变量和计数器
            current += step
            iteration_count += 1
            
            # 避免浮点精度问题
            if step > 0 and current > end + 1e-10:
                break
            if step < 0 and current < end - 1e-10:
                break
                
        logger.debug(f"循环完成: {var} 从 {start} 到 {end}, 步长 {step}, 执行了 {iteration_count} 次")
        return success, image_array, width, height
        
    def process_loop_command(self, param_str, image_array, width, height, line_num=None, process_line_func=None, variables=None):
        """
        处理loop命令（使用分号分隔循环头和循环体）
        
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
                logger.error(f"第 {line_num} 行: 处理循环命令失败，未提供有效的处理函数")
                return False, image_array, width, height
                
            # 使用分号分隔循环头和循环体
            if ';' not in param_str:
                logger.warning(f"第 {line_num} 行: loop语法格式错误，应使用分号分隔循环头和循环体")
                return False, image_array, width, height
            
            loop_header, loop_body = param_str.split(';', 1)
            loop_header = loop_header.strip()
            loop_body = loop_body.strip()
            
            # 解析循环头部参数（变量、起始值、结束值、步长）
            if self.parser:
                header_params = self.parser.parse_params_with_backslash(loop_header, variables)
            else:
                # 简单分割参数（如果没有解析器）
                header_params = loop_header.split('\\')
            
            if len(header_params) < 4:
                logger.warning(f"第 {line_num} 行: loop语法头部需要4个参数（变量、起始值、结束值、步长），实际提供了 {len(header_params)} 个")
                return False, image_array, width, height
            
            # 提取循环参数
            var = header_params[0].strip()
            
            # 处理表达式计算 - 预处理循环参数中的表达式
            if self.expression_evaluator:
                header_params[1] = self.expression_evaluator.process_expression_in_param(header_params[1], variables)
                header_params[2] = self.expression_evaluator.process_expression_in_param(header_params[2], variables)
                header_params[3] = self.expression_evaluator.process_expression_in_param(header_params[3], variables)
            
            try:
                start = float(header_params[1])
                end = float(header_params[2])
                step = float(header_params[3])
            except ValueError:
                logger.warning(f"第 {line_num} 行: 循环参数必须是数值")
                return False, image_array, width, height
                
            # 验证参数
            if not var.isalnum():
                logger.warning(f"第 {line_num} 行: 循环变量必须是字母数字，提供的值: {var}")
                return False, image_array, width, height
                
            if step == 0:
                logger.warning(f"第 {line_num} 行: 步长不能为零")
                return False, image_array, width, height
                
            # 确保start、end、step的方向一致
            if (end - start) * step < 0:
                logger.warning(f"第 {line_num} 行: 步长方向与起始/结束值不一致")
                return False, image_array, width, height
            
            # 处理循环体（可能包含多条用逗号分隔的指令）
            if self.parser:
                instructions = self.parser.parse_instruction_list(loop_body, line_num)
            else:
                # 简单分割指令（如果没有解析器）
                instructions = [i.strip() for i in loop_body.split(',') if i.strip()]
            
            # 计算循环次数（防止无限循环）
            iterations = abs(int((end - start) / step)) + 1
            if iterations > 1000:  # 设置合理的最大循环次数
                logger.warning(f"循环次数过多 ({iterations})，已限制为1000次")
                iterations = 1000
                
            logger.info(f"开始执行循环，变量: {var}，范围: {start} 到 {end}，步长: {step}，总次数: {iterations}")
            
            # 区分不同类型的指令（预处理）
            region_instructions = []
            color_instructions = []
            other_instructions = []
            
            for instr in instructions:
                if instr.startswith("region:"):
                    region_instructions.append(instr)
                elif instr.startswith("color:"):
                    color_instructions.append(instr)
                else:
                    other_instructions.append(instr)
            
            # 复制原始图像数组，防止执行失败时影响原图像
            working_array = np.copy(image_array)
            working_width = width
            working_height = height
            
            # 执行顺序：先颜色、再区域、最后其他指令
            # 这样可以确保颜色和区域在后续指令中可用
            
            # 执行颜色定义指令
            if color_instructions:
                color_success, working_array, working_width, working_height = self.process_loop_iterations(
                    var, start, end, step, color_instructions, 
                    working_array, working_width, working_height, 
                    line_num, process_line_func, "颜色", variables
                )
            else:
                color_success = True
                
            # 执行区域定义指令
            if region_instructions:
                region_success, working_array, working_width, working_height = self.process_loop_iterations(
                    var, start, end, step, region_instructions, 
                    working_array, working_width, working_height, 
                    line_num, process_line_func, "区域", variables
                )
            else:
                region_success = True
            
            # 执行其他指令
            if other_instructions:
                other_success, working_array, working_width, working_height = self.process_loop_iterations(
                    var, start, end, step, other_instructions, 
                    working_array, working_width, working_height, 
                    line_num, process_line_func, "其他", variables
                )
            else:
                other_success = True
                
            # 如果所有部分都执行成功，返回更新后的图像
            if color_success and region_success and other_success:
                return True, working_array, working_width, working_height
            else:
                # 至少有一部分失败，但仍然返回最新结果
                logger.warning("循环执行部分失败，但继续处理")
                return False, working_array, working_width, working_height
                
        except Exception as e:
            logger.error(f"执行循环时出错: {str(e)}")
            logger.debug(traceback.format_exc())
            return False, image_array, width, height 