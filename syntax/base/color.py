from .base import PixelSyntax, logger

class ColorSyntax(PixelSyntax):
    """颜色定义语法类，用于定义可重用的颜色"""
    
    # 颜色字典，全局共享
    color_registry = {}
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "color"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - id: 颜色的唯一标识符
                - r: 红色通道值（0-255）
                - g: 绿色通道值（0-255）
                - b: 蓝色通道值（0-255）
                - a: 透明度（0-255，可选，默认为255）
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) < 4 or len(params) > 5:
            logger.warning(f"第 {line_num} 行: color语法需要4或5个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            color_id = str(params[0])
            r = int(params[1])
            g = int(params[2])
            b = int(params[3])
            a = 255 if len(params) < 5 else int(params[4])
            
            # 验证参数
            if not color_id:
                logger.warning(f"第 {line_num} 行: 颜色ID不能为空")
                return None
                
            if not self._is_valid_rgb(r, g, b) or not (0 <= a <= 255):
                logger.warning(f"第 {line_num} 行: 颜色值必须在0-255范围内，提供的值: {r},{g},{b},{a}")
                # 自动修正颜色值
                r = self._clamp_rgb(r)
                g = self._clamp_rgb(g)
                b = self._clamp_rgb(b)
                a = self._clamp_rgb(a)
                logger.info(f"第 {line_num} 行: 颜色值已自动修正为: {r},{g},{b},{a}")
            
            # 返回解析后的参数
            return {
                "id": color_id,
                "r": r,
                "g": g,
                "b": b,
                "a": a
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params):
        """
        注册颜色到全局颜色注册表
        
        Args:
            image_array: 图像数组（不会被修改）
            width: 图像宽度
            height: 图像高度
            params: 已解析的参数
            
        Returns:
            (成功/失败, 图像数组, 宽度, 高度)的元组
        """
        try:
            # 提取参数
            color_id = params["id"]
            r = params["r"]
            g = params["g"]
            b = params["b"]
            a = params["a"]
            
            # 注册颜色
            ColorSyntax.color_registry[color_id] = (r, g, b, a)
            logger.info(f"已定义颜色: {color_id} = ({r},{g},{b},{a})")
            
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"注册颜色时出错: {str(e)}")
            return False, image_array, width, height
    
    @classmethod
    def get_color(cls, color_id):
        """
        获取已注册的颜色
        
        Args:
            color_id: 颜色标识符
            
        Returns:
            颜色元组 (r,g,b,a) 或 None（如果未找到）
        """
        return cls.color_registry.get(color_id) 