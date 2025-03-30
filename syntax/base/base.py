import numpy as np
import logging

# 获取日志记录器
logger = logging.getLogger('pixel_image_generator')

class PixelSyntax:
    """像素语法基类，所有具体语法都应继承此类"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称（由子类实现）"""
        raise NotImplementedError("子类必须实现get_name方法")
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表（由子类实现）
        
        Args:
            params: 参数列表
            line_num: 行号（用于日志）
            
        Returns:
            True表示参数有效，False表示参数无效
        """
        raise NotImplementedError("子类必须实现parse_params方法")
    
    def apply(self, image_array, width, height, params):
        """
        应用语法效果到图像数组
        
        Args:
            image_array: 图像数组（RGBA格式）
            width: 图像宽度
            height: 图像高度
            params: 已解析的参数
            
        Returns:
            True表示应用成功，False表示应用失败
        """
        raise NotImplementedError("子类必须实现apply方法")
    
    def get_syntax_processor(self):
        """
        获取语法处理器实例
        
        Returns:
            语法处理器实例或None
        """
        # 通过上下文访问语法处理器实例
        # 因为语法类是在SyntaxProcessor中实例化的，所以可以通过self获取
        if hasattr(self, 'syntax_processor'):
            return self.syntax_processor
            
        import inspect
        current_frame = inspect.currentframe()
        while current_frame:
            if 'self' in current_frame.f_locals and hasattr(current_frame.f_locals['self'], 'variables'):
                # 检查是否有变量字典，这是SyntaxProcessor的特征
                return current_frame.f_locals['self']
            current_frame = current_frame.f_back
            
        return None
    
    def _is_valid_coordinate(self, x, y, width, height):
        """检查坐标是否在图像范围内"""
        return 0 <= x < width and 0 <= y < height
    
    def _is_valid_rgb(self, r, g, b):
        """检查RGB值是否有效"""
        return (isinstance(r, int) and 0 <= r <= 255 and
                isinstance(g, int) and 0 <= g <= 255 and
                isinstance(b, int) and 0 <= b <= 255)
    
    def _clamp_rgb(self, value):
        """将值限制在RGB范围内(0-255)"""
        return max(0, min(255, int(value)))
    
    def _set_pixel(self, image_array, x, y, r, g, b, alpha=255):
        """设置像素RGBA值（带边界检查）"""
        height, width = image_array.shape[:2]
        if 0 <= x < width and 0 <= y < height:
            # 确保RGB值在有效范围内
            r = self._clamp_rgb(r)
            g = self._clamp_rgb(g)
            b = self._clamp_rgb(b)
            alpha = self._clamp_rgb(alpha)
            
            # 设置像素值
            image_array[y, x, 0] = r
            image_array[y, x, 1] = g
            image_array[y, x, 2] = b
            image_array[y, x, 3] = alpha

    def _blend_pixel(self, image_array, x, y, r, g, b, alpha=255):
        """混合像素RGBA值（考虑透明度）"""
        height, width = image_array.shape[:2]
        if 0 <= x < width and 0 <= y < height:
            # 确保RGB值在有效范围内
            r = self._clamp_rgb(r)
            g = self._clamp_rgb(g)
            b = self._clamp_rgb(b)
            alpha = self._clamp_rgb(alpha) / 255.0
            
            # 读取当前像素值
            curr_r = float(image_array[y, x, 0])
            curr_g = float(image_array[y, x, 1])
            curr_b = float(image_array[y, x, 2])
            curr_a = float(image_array[y, x, 3]) / 255.0
            
            # Alpha混合
            if alpha > 0:
                new_a = alpha + curr_a * (1 - alpha)
                if new_a > 0:
                    new_r = (r * alpha + curr_r * curr_a * (1 - alpha)) / new_a
                    new_g = (g * alpha + curr_g * curr_a * (1 - alpha)) / new_a
                    new_b = (b * alpha + curr_b * curr_a * (1 - alpha)) / new_a
                else:
                    new_r, new_g, new_b = 0, 0, 0
                
                # 设置像素值
                image_array[y, x, 0] = self._clamp_rgb(new_r)
                image_array[y, x, 1] = self._clamp_rgb(new_g)
                image_array[y, x, 2] = self._clamp_rgb(new_b)
                image_array[y, x, 3] = self._clamp_rgb(new_a * 255) 