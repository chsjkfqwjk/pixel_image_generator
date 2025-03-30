#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
像素图像生成器 - 高级语法模块包
版本: 3.0.0

此包包含像素图像生成器的高级语法解析和处理功能:
- 条件语句 (if)
- 循环语句 (loop)
- 复杂表达式解析
- 变量处理和替换
- 嵌套结构处理
"""

from .processor import AdvancedSyntaxProcessor
from .expression.evaluator import ExpressionEvaluator
from .control.conditions import ConditionEvaluator
from .control.loops import LoopProcessor

__version__ = "3.0.0"

__all__ = [
    'AdvancedSyntaxProcessor',
    'ExpressionEvaluator',
    'ConditionEvaluator',
    'LoopProcessor'
] 