"""
基础语法模块，包含所有像素图像生成器的语法处理器。
"""

# 像素图像生成器语法包
# 此包包含所有支持的语法类型定义

# 导入基础语法类
from .config import ConfigSyntax
from .color import ColorSyntax
from .fill import FillSyntax
from .points import PointsSyntax
from .path import PathSyntax
from .gradient import GradientSyntax
from .region import RegionSyntax
from .transform import TransformSyntax
from .variable import VarSyntax

# 版本信息
__version__ = "3.0.0"

# 导出所有语法类
SYNTAX_CLASSES = [
    ConfigSyntax,
    ColorSyntax,
    FillSyntax,
    PointsSyntax,
    PathSyntax,
    GradientSyntax,
    RegionSyntax,
    TransformSyntax,
    VarSyntax,
] 