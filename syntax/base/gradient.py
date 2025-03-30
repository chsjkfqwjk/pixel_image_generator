from .base import PixelSyntax, logger
from .region import RegionSyntax
from .color import ColorSyntax
import numpy as np
import math

class GradientSyntax(PixelSyntax):
    """渐变填充语法类，用于在区域内绘制渐变"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "gradient"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - region_id: 要填充的区域ID
                - type: 渐变类型（linear、radial、conical）
                - point1: 渐变起始点，格式为"x1|y1"
                - point2: 渐变结束点，格式为"x2|y2"
                - color1_id: 起始颜色ID
                - color2_id: 结束颜色ID
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) != 6:
            logger.warning(f"第 {line_num} 行: gradient语法需要6个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            region_id = str(params[0])
            gradient_type = str(params[1]).lower()
            
            # 解析坐标点
            point1_str = str(params[2])
            point2_str = str(params[3])
            
            # 解析点1 (x1|y1)
            try:
                if '|' in point1_str:
                    x1_str, y1_str = point1_str.split('|')
                    x1 = int(x1_str.strip())
                    y1 = int(y1_str.strip())
                else:
                    logger.warning(f"第 {line_num} 行: 点1格式错误，应为'x|y'")
                    return None
            except Exception as e:
                logger.warning(f"第 {line_num} 行: 点1解析错误: {str(e)}")
                return None
                
            # 解析点2 (x2|y2)
            try:
                if '|' in point2_str:
                    x2_str, y2_str = point2_str.split('|')
                    x2 = int(x2_str.strip())
                    y2 = int(y2_str.strip())
                else:
                    logger.warning(f"第 {line_num} 行: 点2格式错误，应为'x|y'")
                    return None
            except Exception as e:
                logger.warning(f"第 {line_num} 行: 点2解析错误: {str(e)}")
                return None
            
            color1_id = str(params[4])
            color2_id = str(params[5])
            
            # 验证区域ID
            region = RegionSyntax.get_region(region_id)
            if not region:
                logger.warning(f"第 {line_num} 行: 未找到区域 '{region_id}'")
                return None
                
            # 验证渐变类型
            valid_types = ["linear", "radial", "conical"]
            if gradient_type not in valid_types:
                logger.warning(f"第 {line_num} 行: 不支持的渐变类型 '{gradient_type}'，有效值: {valid_types}")
                return None
                
            # 验证颜色ID
            color1 = ColorSyntax.get_color(color1_id)
            if not color1:
                logger.warning(f"第 {line_num} 行: 未找到颜色 '{color1_id}'")
                return None
                
            color2 = ColorSyntax.get_color(color2_id)
            if not color2:
                logger.warning(f"第 {line_num} 行: 未找到颜色 '{color2_id}'")
                return None
            
            # 返回解析后的参数
            return {
                "region_id": region_id,
                "type": gradient_type,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "color1_id": color1_id,
                "color2_id": color2_id
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params):
        """
        应用渐变填充效果
        
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
            gradient_type = params["type"]
            x1 = params["x1"]
            y1 = params["y1"]
            x2 = params["x2"]
            y2 = params["y2"]
            color1_id = params["color1_id"]
            color2_id = params["color2_id"]
            
            # 获取区域和颜色
            region = RegionSyntax.get_region(region_id)
            color1 = ColorSyntax.get_color(color1_id)
            color2 = ColorSyntax.get_color(color2_id)
            
            if not region or not color1 or not color2:
                return False, image_array, width, height
            
            # 提取区域信息
            region_x1 = region["x1"]
            region_y1 = region["y1"]
            region_x2 = region["x2"]
            region_y2 = region["y2"]
            mask = region["mask"]
            
            # 区域宽高
            region_width = region_x2 - region_x1 + 1
            region_height = region_y2 - region_y1 + 1
            
            # 将坐标相对于区域调整
            x1 = max(0, min(region_width - 1, x1))
            y1 = max(0, min(region_height - 1, y1))
            x2 = max(0, min(region_width - 1, x2))
            y2 = max(0, min(region_height - 1, y2))
            
            # 提取颜色
            r1, g1, b1, a1 = color1
            r2, g2, b2, a2 = color2
            
            # 确保区域在图像范围内
            if region_x1 >= width or region_y1 >= height or region_x2 < 0 or region_y2 < 0:
                logger.warning(f"区域 {region_id} 在图像范围外，已跳过")
                return True, image_array, width, height
            
            # 裁剪区域至图像范围
            mask_xstart = 0
            mask_ystart = 0
            
            if region_x1 < 0:
                mask_xstart = -region_x1
                region_x1 = 0
            
            if region_y1 < 0:
                mask_ystart = -region_y1
                region_y1 = 0
            
            xend = min(region_x2 + 1, width)
            yend = min(region_y2 + 1, height)
            
            # 获取实际绘制区域的宽高
            draw_width = xend - region_x1
            draw_height = yend - region_y1
            
            # 如果绘制区域无效，跳过
            if draw_width <= 0 or draw_height <= 0:
                return True, image_array, width, height
            
            # 获取有效掩码部分
            valid_mask = mask[mask_ystart:mask_ystart + draw_height, mask_xstart:mask_xstart + draw_width]
            
            # 根据渐变类型应用渐变
            if gradient_type == "linear":
                self._apply_linear_gradient(image_array, region_x1, region_y1, draw_width, draw_height,
                                           x1, y1, x2, y2, r1, g1, b1, a1, r2, g2, b2, a2,
                                           valid_mask)
            elif gradient_type == "radial":
                self._apply_radial_gradient(image_array, region_x1, region_y1, draw_width, draw_height,
                                           x1, y1, x2, y2, r1, g1, b1, a1, r2, g2, b2, a2,
                                           valid_mask)
            else:  # 默认使用线性渐变
                self._apply_linear_gradient(image_array, region_x1, region_y1, draw_width, draw_height,
                                           x1, y1, x2, y2, r1, g1, b1, a1, r2, g2, b2, a2,
                                           valid_mask)
            
            logger.info(f"已应用 {gradient_type} 渐变填充到区域 {region_id}")
            
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"渐变填充时出错: {str(e)}")
            return False, image_array, width, height
    
    def _apply_linear_gradient(self, image_array, x_offset, y_offset, width, height,
                              x1, y1, x2, y2, r1, g1, b1, a1, r2, g2, b2, a2, mask):
        """应用线性渐变"""
        # 计算渐变向量
        dx = x2 - x1
        dy = y2 - y1
        
        # 渐变线长度的平方
        gradient_length_squared = dx * dx + dy * dy
        
        if gradient_length_squared == 0:
            # 防止除零错误
            gradient_length_squared = 1
        
        # 对每个像素应用渐变
        for y in range(height):
            for x in range(width):
                if mask[y, x]:
                    # 计算像素在图像中的绝对坐标
                    abs_x = x + x_offset
                    abs_y = y + y_offset
                    
                    # 计算像素到起点的向量
                    px = abs_x - x1
                    py = abs_y - y1
                    
                    # 计算投影比例 (0.0 ~ 1.0)
                    t = max(0.0, min(1.0, (px * dx + py * dy) / gradient_length_squared))
                    
                    # 计算混合颜色
                    r = int(r1 + t * (r2 - r1))
                    g = int(g1 + t * (g2 - g1))
                    b = int(b1 + t * (b2 - b1))
                    a = int(a1 + t * (a2 - a1))
                    
                    # 裁剪到有效范围
                    r = self._clamp_rgb(r)
                    g = self._clamp_rgb(g)
                    b = self._clamp_rgb(b)
                    a = self._clamp_rgb(a)
                    
                    # 设置像素颜色
                    self._blend_pixel(image_array, abs_x, abs_y, r, g, b, a)
    
    def _apply_radial_gradient(self, image_array, x_offset, y_offset, width, height,
                              x1, y1, x2, y2, r1, g1, b1, a1, r2, g2, b2, a2, mask):
        """应用径向渐变"""
        # 计算渐变半径
        radius = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        if radius == 0:
            # 防止除零错误
            radius = 1
        
        # 对每个像素应用渐变
        for y in range(height):
            for x in range(width):
                if mask[y, x]:
                    # 计算像素在图像中的绝对坐标
                    abs_x = x + x_offset
                    abs_y = y + y_offset
                    
                    # 计算到中心的距离
                    distance = math.sqrt((abs_x - x1) ** 2 + (abs_y - y1) ** 2)
                    
                    # 计算比例 (0.0 ~ 1.0)
                    t = max(0.0, min(1.0, distance / radius))
                    
                    # 计算混合颜色
                    r = int(r1 + t * (r2 - r1))
                    g = int(g1 + t * (g2 - g1))
                    b = int(b1 + t * (b2 - b1))
                    a = int(a1 + t * (a2 - a1))
                    
                    # 裁剪到有效范围
                    r = self._clamp_rgb(r)
                    g = self._clamp_rgb(g)
                    b = self._clamp_rgb(b)
                    a = self._clamp_rgb(a)
                    
                    # 设置像素颜色
                    self._blend_pixel(image_array, abs_x, abs_y, r, g, b, a)
    
    def _apply_conical_gradient(self, image_array, x_offset, y_offset, width, height,
                               x1, y1, r1, g1, b1, a1, r2, g2, b2, a2, mask):
        """应用圆锥渐变"""
        # 对每个像素应用渐变
        for y in range(height):
            for x in range(width):
                if mask[y, x]:
                    # 计算像素在图像中的绝对坐标
                    abs_x = x + x_offset
                    abs_y = y + y_offset
                    
                    # 计算到中心的角度 (0 ~ 2π)
                    angle = math.atan2(abs_y - y1, abs_x - x1)
                    if angle < 0:
                        angle += 2 * math.pi
                    
                    # 计算比例 (0.0 ~ 1.0)
                    t = angle / (2 * math.pi)
                    
                    # 计算混合颜色
                    r = int(r1 + t * (r2 - r1))
                    g = int(g1 + t * (g2 - g1))
                    b = int(b1 + t * (b2 - b1))
                    a = int(a1 + t * (a2 - a1))
                    
                    # 裁剪到有效范围
                    r = self._clamp_rgb(r)
                    g = self._clamp_rgb(g)
                    b = self._clamp_rgb(b)
                    a = self._clamp_rgb(a)
                    
                    # 设置像素颜色
                    self._blend_pixel(image_array, abs_x, abs_y, r, g, b, a) 