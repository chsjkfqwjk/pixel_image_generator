#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
像素图像生成器 - 高级语法模块
版本: 3.0.0

此模块用于兼容性，将导出advanced包中的功能
"""

import logging
import sys
import os

# 添加当前目录到路径，确保能够导入advanced包
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入高级语法处理器
try:
    from advanced.processor import AdvancedSyntaxProcessor
    from advanced.expression.evaluator import ExpressionEvaluator
    from advanced.expression.ternary import TernaryEvaluator
    from advanced.control.conditions import ConditionEvaluator
    from advanced.control.loops import LoopProcessor
    
    logger = logging.getLogger('pixel_image_generator')
    logger.info("高级语法模块已从advanced包导出")
except ImportError as e:
    import traceback
    logger = logging.getLogger('pixel_image_generator')
    logger.error(f"导入高级语法模块失败: {str(e)}")
    logger.debug(traceback.format_exc())

    # 定义一个空的AdvancedSyntaxProcessor类，防止导入失败时程序崩溃
    class AdvancedSyntaxProcessor:
        """高级语法处理器（兼容类）"""
    
        def __init__(self):
            """初始化高级语法处理器"""
            self.variables = {}
            self._expr_cache = {}
            logger.warning("使用的是兼容模式的AdvancedSyntaxProcessor，功能受限")
        
        def process_if_command(self, *args, **kwargs):
            """处理if命令（兼容方法）"""
            logger.error("高级语法模块未正确加载，if命令不可用")
            return False, args[1], args[2], args[3]
        
        def process_loop_command(self, *args, **kwargs):
            """处理loop命令（兼容方法）"""
            logger.error("高级语法模块未正确加载，loop命令不可用")
            return False, args[1], args[2], args[3]
        
        def process_comma_separated_instructions(self, *args, **kwargs):
            """处理逗号分隔的多条指令（兼容方法）"""
            logger.error("高级语法模块未正确加载，多条指令处理不可用")
            return False, args[1], args[2], args[3]
        
        def parse_params_with_backslash(self, param_str):
            """使用反斜杠分隔参数（兼容方法）"""
            return param_str.split('\\')
    
        def replace_variable_in_instruction(self, instruction, var_name, var_value):
            """替换指令中的变量（兼容方法）"""
            return instruction.replace(str(var_name), str(var_value))
    
        def clear_expr_cache(self):
            """清除表达式计算缓存（兼容方法）"""
            self._expr_cache.clear()

# 确保导出与原始类兼容的接口
__all__ = ['AdvancedSyntaxProcessor']
