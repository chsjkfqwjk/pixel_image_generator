import numpy as np
from .base import PixelSyntax, logger

class ConfigSyntax(PixelSyntax):
    """配置图像语法类，用于设置图像的宽度、高度和背景色"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "config"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - width: 画布宽度（像素）
                - height: 画布高度（像素）
                - bg_r: 背景色红色通道值（0-255）
                - bg_g: 背景色绿色通道值（0-255）
                - bg_b: 背景色蓝色通道值（0-255）
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) != 5:
            logger.warning(f"第 {line_num} 行: config语法需要5个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            width = int(params[0])
            height = int(params[1])
            bg_r = int(params[2])
            bg_g = int(params[3])
            bg_b = int(params[4])
            
            # 验证参数
            if width <= 0 or height <= 0:
                logger.warning(f"第 {line_num} 行: 图像尺寸必须为正数，提供的值: {width}x{height}")
                return None
                
            if not self._is_valid_rgb(bg_r, bg_g, bg_b):
                logger.warning(f"第 {line_num} 行: RGB值必须在0-255范围内，提供的值: {bg_r},{bg_g},{bg_b}")
                # 自动修正RGB值
                bg_r = self._clamp_rgb(bg_r)
                bg_g = self._clamp_rgb(bg_g)
                bg_b = self._clamp_rgb(bg_b)
                logger.info(f"第 {line_num} 行: RGB值已自动修正为: {bg_r},{bg_g},{bg_b}")
            
            # 返回解析后的参数
            return {
                "width": width,
                "height": height,
                "bg_r": bg_r,
                "bg_g": bg_g,
                "bg_b": bg_b
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params):
        """
        应用配置到图像
        
        Args:
            image_array: 图像数组（可能会被忽略，根据配置创建新的数组）
            width: 原始宽度（可能会被覆盖）
            height: 原始高度（可能会被覆盖）
            params: 已解析的参数
            
        Returns:
            新的图像数组、宽度和高度
        """
        try:
            # 创建新的图像数组
            new_width = params["width"]
            new_height = params["height"]
            bg_r = params["bg_r"]
            bg_g = params["bg_g"]
            bg_b = params["bg_b"]
            
            # 创建RGBA图像数组
            new_image = np.zeros((new_height, new_width, 4), dtype=np.uint8)
            
            # 设置背景色
            new_image[:, :, 0] = bg_r  # R
            new_image[:, :, 1] = bg_g  # G
            new_image[:, :, 2] = bg_b  # B
            new_image[:, :, 3] = 255   # A (完全不透明)
            
            logger.info(f"已配置图像: {new_width}x{new_height}, 背景色: ({bg_r},{bg_g},{bg_b})")
            
            # 返回新的图像数组和尺寸
            return True, new_image, new_width, new_height
            
        except Exception as e:
            logger.error(f"应用配置时出错: {str(e)}")
            return False, image_array, width, height 