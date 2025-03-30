from .base import PixelSyntax, logger
from .region import RegionSyntax
from .color import ColorSyntax
import numpy as np

class FillSyntax(PixelSyntax):
    """填充区域语法类，用于用指定颜色填充区域"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "fill"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - region_id: 要填充的区域ID
                - color_id: 使用的颜色ID
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) != 2:
            logger.warning(f"第 {line_num} 行: fill语法需要2个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            region_id = str(params[0])
            color_id = str(params[1])
            
            # 验证区域ID
            region = RegionSyntax.get_region(region_id)
            if not region:
                logger.warning(f"第 {line_num} 行: 未找到区域 '{region_id}'")
                return None
                
            # 验证颜色ID
            color = ColorSyntax.get_color(color_id)
            if not color:
                logger.warning(f"第 {line_num} 行: 未找到颜色 '{color_id}'")
                return None
            
            # 返回解析后的参数
            return {
                "region_id": region_id,
                "color_id": color_id
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params):
        """
        用指定颜色填充区域
        
        Args:
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            params: 已解析的参数
            
        Returns:
            (成功/失败, 图像数组, 宽度, 高度)的元组
        """
        try:
            # 提取参数
            region_id = params["region_id"]
            color_id = params["color_id"]
            
            # 获取区域和颜色
            region = RegionSyntax.get_region(region_id)
            color = ColorSyntax.get_color(color_id)
            
            if not region or not color:
                return False, image_array, width, height
            
            # 提取区域信息
            x1 = region["x1"]
            y1 = region["y1"]
            x2 = region["x2"]
            y2 = region["y2"]
            mask = region["mask"]
            
            # 提取颜色
            r, g, b, a = color
            
            # 区域宽高
            region_width = x2 - x1 + 1
            region_height = y2 - y1 + 1
            
            # 确保区域在图像范围内
            if x1 >= width or y1 >= height or x2 < 0 or y2 < 0:
                logger.warning(f"区域 {region_id} 在图像范围外，已跳过")
                return True, image_array, width, height
            
            # 裁剪区域至图像范围
            mask_xstart = 0
            mask_ystart = 0
            
            if x1 < 0:
                mask_xstart = -x1
                x1 = 0
            
            if y1 < 0:
                mask_ystart = -y1
                y1 = 0
            
            xend = min(x2 + 1, width)
            yend = min(y2 + 1, height)
            
            # 获取实际绘制区域的宽高
            draw_width = xend - x1
            draw_height = yend - y1
            
            # 如果绘制区域无效，跳过
            if draw_width <= 0 or draw_height <= 0:
                return True, image_array, width, height
            
            # 获取有效掩码部分
            valid_mask = mask[mask_ystart:mask_ystart + draw_height, mask_xstart:mask_xstart + draw_width]
            
            # 填充区域
            if a == 255:  # 完全不透明
                image_array[y1:yend, x1:xend, 0][valid_mask] = r
                image_array[y1:yend, x1:xend, 1][valid_mask] = g
                image_array[y1:yend, x1:xend, 2][valid_mask] = b
                image_array[y1:yend, x1:xend, 3][valid_mask] = a
            else:  # 半透明
                # 获取当前像素
                curr_pixels = image_array[y1:yend, x1:xend].copy()
                
                # 计算alpha混合比例
                alpha = a / 255.0
                
                # 创建新颜色
                new_pixels = curr_pixels.copy()
                new_pixels[..., 0][valid_mask] = r
                new_pixels[..., 1][valid_mask] = g
                new_pixels[..., 2][valid_mask] = b
                new_pixels[..., 3][valid_mask] = a
                
                # 混合
                blend_mask = valid_mask & (curr_pixels[..., 3] > 0)
                
                # 应用alpha混合
                mixed_pixels = alpha * new_pixels[..., :3] + (1 - alpha) * curr_pixels[..., :3]
                image_array[y1:yend, x1:xend, :3][blend_mask] = mixed_pixels[blend_mask]
                
                # 更新alpha通道
                image_array[y1:yend, x1:xend, 3][valid_mask] = np.maximum(
                    image_array[y1:yend, x1:xend, 3][valid_mask],
                    a
                )
            
            logger.info(f"已填充区域: {region_id} 使用颜色: {color_id}")
            
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"填充区域时出错: {str(e)}")
            return False, image_array, width, height 