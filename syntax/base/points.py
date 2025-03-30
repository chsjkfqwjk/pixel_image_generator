from .base import PixelSyntax, logger
from .region import RegionSyntax
from .color import ColorSyntax
import numpy as np
import random

class PointsSyntax(PixelSyntax):
    """点阵绘制语法类，用于在区域内按指定模式绘制点"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "points"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - region_id: 要绘制的区域ID
                - color_id: 使用的颜色ID
                - pattern: 绘制模式（random、grid、noise）
                - density: 点密度（0-1）
                - param1: 模式参数（可选，网格间距、噪声频率等）
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) < 4 or len(params) > 5:
            logger.warning(f"第 {line_num} 行: points语法需要4-5个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            region_id = str(params[0])
            color_id = str(params[1])
            pattern = str(params[2]).lower()
            density = float(params[3])
            param1 = 0 if len(params) < 5 else float(params[4])
            
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
                
            # 验证模式
            valid_patterns = ["random", "grid", "noise"]
            if pattern not in valid_patterns:
                logger.warning(f"第 {line_num} 行: 不支持的绘制模式 '{pattern}'，有效值: {valid_patterns}")
                return None
                
            # 验证密度
            if not (0 <= density <= 1):
                logger.warning(f"第 {line_num} 行: 密度必须在0-1范围内，提供的值: {density}")
                density = max(0, min(1, density))
                logger.info(f"第 {line_num} 行: 密度已自动修正为: {density}")
            
            # 返回解析后的参数
            return {
                "region_id": region_id,
                "color_id": color_id,
                "pattern": pattern,
                "density": density,
                "param1": param1
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params):
        """
        在区域内绘制点阵
        
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
            pattern = params["pattern"]
            density = params["density"]
            param1 = params["param1"]
            
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
            
            # 根据模式绘制点
            if pattern == "random":
                self._draw_random_points(image_array, x1, y1, draw_width, draw_height, 
                                         r, g, b, a, density, valid_mask)
            elif pattern == "grid":
                self._draw_grid_points(image_array, x1, y1, draw_width, draw_height, 
                                      r, g, b, a, density, param1, valid_mask)
            elif pattern == "noise":
                self._draw_noise_points(image_array, x1, y1, draw_width, draw_height, 
                                       r, g, b, a, density, param1, valid_mask)
            
            logger.info(f"已在区域 {region_id} 绘制 {pattern} 点阵，密度: {density}")
            
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"绘制点阵时出错: {str(e)}")
            return False, image_array, width, height
    
    def _draw_random_points(self, image_array, x_offset, y_offset, width, height, 
                           r, g, b, a, density, mask):
        """绘制随机分布的点"""
        # 计算点数
        total_pixels = np.sum(mask)
        num_points = int(total_pixels * density)
        
        # 找出掩码中为True的像素坐标
        y_coords, x_coords = np.where(mask)
        
        if len(y_coords) == 0:
            return
        
        # 随机选择num_points个点
        if num_points > 0:
            indices = np.random.choice(len(y_coords), min(num_points, len(y_coords)), replace=False)
            
            # 绘制选中的点
            for idx in indices:
                y = y_coords[idx]
                x = x_coords[idx]
                
                # 计算绝对坐标
                abs_x = x + x_offset
                abs_y = y + y_offset
                
                # 设置像素颜色
                self._blend_pixel(image_array, abs_x, abs_y, r, g, b, a)
    
    def _draw_grid_points(self, image_array, x_offset, y_offset, width, height, 
                         r, g, b, a, density, grid_size, mask):
        """绘制网格分布的点"""
        # 计算网格大小（根据密度）
        if grid_size <= 0:
            # 如果没有指定网格大小，根据密度计算
            grid_size = max(1, int(1.0 / density))
        
        # 遍历所有可能的网格点
        for grid_y in range(0, height, max(1, int(grid_size))):
            for grid_x in range(0, width, max(1, int(grid_size))):
                # 检查点是否在掩码范围内
                if grid_y < mask.shape[0] and grid_x < mask.shape[1] and mask[grid_y, grid_x]:
                    # 计算绝对坐标
                    abs_x = grid_x + x_offset
                    abs_y = grid_y + y_offset
                    
                    # 设置像素颜色
                    self._blend_pixel(image_array, abs_x, abs_y, r, g, b, a)
    
    def _draw_noise_points(self, image_array, x_offset, y_offset, width, height, 
                          r, g, b, a, density, frequency, mask):
        """绘制基于噪声的点分布"""
        # 如果频率为0，默认使用合理值
        if frequency <= 0:
            frequency = 0.1
        
        # 为了生成连贯的噪声，使用noise_seed
        noise_seed = int(random.random() * 10000)
        random.seed(noise_seed)
        
        # 生成柏林噪声的简化版本
        noise = np.zeros((height, width))
        
        # 对每个像素进行采样
        for y in range(height):
            for x in range(width):
                # 简化的噪声函数
                noise_val = random.random()  # 真实柏林噪声更复杂，这里简化处理
                noise[y, x] = noise_val
        
        # 设置阈值，只有噪声值超过阈值的点才会被绘制
        threshold = 1.0 - density
        
        # 绘制噪声点
        for y in range(height):
            for x in range(width):
                # 检查点是否在掩码范围内
                if y < mask.shape[0] and x < mask.shape[1] and mask[y, x]:
                    if noise[y, x] > threshold:
                        # 计算绝对坐标
                        abs_x = x + x_offset
                        abs_y = y + y_offset
                        
                        # 设置像素颜色
                        self._blend_pixel(image_array, abs_x, abs_y, r, g, b, a)
        
        # 重置随机数种子
        random.seed() 