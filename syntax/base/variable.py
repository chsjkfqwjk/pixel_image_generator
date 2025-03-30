#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
变量语法处理器，用于处理变量定义和赋值语法
"""

import logging
import re
import numpy as np
from .base import PixelSyntax

logger = logging.getLogger('pixel_image_generator')

class VarSyntax(PixelSyntax):
    """变量语法处理器，处理变量定义和赋值"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "var"
    
    def parse_params(self, params, line_num=None):
        """解析参数"""
        if len(params) < 2:
            logger.warning(f"第 {line_num} 行: var语法需要至少2个参数（变量名和值），实际提供了 {len(params)} 个")
            return None
            
        var_name = params[0]
        var_value = params[1]
        
        # 检查变量名是否合法
        if not self._is_valid_var_name(var_name):
            logger.warning(f"第 {line_num} 行: 变量名 '{var_name}' 不合法，只能包含字母、数字和下划线，且不能以数字开头")
            return None
            
        return {
            "var_name": var_name,
            "var_value": var_value
        }
        
    def apply(self, image_array, width, height, params):
        """应用语法，设置变量值"""
        var_name = params["var_name"]
        var_value = params["var_value"]
        
        # 处理表达式中的变量引用
        if isinstance(var_value, str) and "${" in var_value:
            # 实际处理在高级模块中完成，这里只进行简单的赋值
            pass
        
        # 尝试将数值型变量转换为对应的类型
        try:
            # 如果是整数
            if re.match(r"^-?\d+$", str(var_value)):
                var_value = int(var_value)
            # 如果是浮点数
            elif re.match(r"^-?\d+\.\d+$", str(var_value)):
                var_value = float(var_value)
        except (ValueError, TypeError):
            # 如果转换失败，保持原样
            pass
            
        # 添加到语法处理器的变量列表
        syntax_processor = self.get_syntax_processor()
        if syntax_processor:
            syntax_processor.variables[var_name] = var_value
            logger.info(f"已设置变量: {var_name} = {var_value}")
        else:
            logger.warning(f"无法设置变量: {var_name}，未找到语法处理器")
            return False, image_array, width, height
            
        return True, image_array, width, height
        
    def _is_valid_var_name(self, name):
        """检查变量名是否合法"""
        return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name) is not None