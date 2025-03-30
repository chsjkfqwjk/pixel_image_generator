from .base import PixelSyntax, logger
from .color import ColorSyntax
import numpy as np
import math

class PathSyntax(PixelSyntax):
    """路径绘制语法类，用于绘制连接点的路径"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "path"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - points_list: 点列表，用"x1|y1-x2|y2-..."表示
                - color_id: 使用的颜色ID
                - thickness: 线条粗细（可选，默认为1）
                - style: 线条样式（可选，默认为solid，支持solid、dashed、wave）
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) < 2 or len(params) > 4:
            logger.warning(f"第 {line_num} 行: path语法需要2-4个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            points_list_str = str(params[0])
            color_id = str(params[1])
            thickness = 1 if len(params) < 3 else int(params[2])
            style = "solid" if len(params) < 4 else str(params[3]).lower()
            
            # 解析点列表
            points = []
            try:
                # 处理多个点组 - 使用短横线分隔
                if "-" in points_list_str:
                    point_groups = points_list_str.split('-')
                    for group in point_groups:
                        if '|' in group:
                            x_str, y_str = group.split('|')
                            x = int(x_str.strip())
                            y = int(y_str.strip())
                            points.append((x, y))
                # 处理单个点 - 使用竖线分隔
                elif '|' in points_list_str:
                    x_str, y_str = points_list_str.split('|')
                    x = int(x_str.strip())
                    y = int(y_str.strip())
                    points.append((x, y))
                    # 至少需要两个点，所以如果只有一个点，创建一个重复点
                    points.append((x, y))
            except Exception as e:
                logger.warning(f"第 {line_num} 行: 点列表格式错误: {str(e)}")
                return None
            
            # 验证点列表
            if len(points) < 2:
                logger.warning(f"第 {line_num} 行: 路径需要至少2个点，实际提供了 {len(points)} 个")
                return None
                
            # 验证颜色ID
            color = ColorSyntax.get_color(color_id)
            if not color:
                logger.warning(f"第 {line_num} 行: 未找到颜色 '{color_id}'")
                return None
                
            # 验证线条粗细
            if thickness < 1:
                logger.warning(f"第 {line_num} 行: 线条粗细必须大于0，提供的值: {thickness}")
                thickness = max(1, thickness)
                logger.info(f"第 {line_num} 行: 线条粗细已自动修正为: {thickness}")
                
            # 验证线条样式
            valid_styles = ["solid", "dashed", "wave", "closed"]
            if style not in valid_styles:
                logger.warning(f"第 {line_num} 行: 不支持的线条样式 '{style}'，有效值: {valid_styles}")
                logger.info(f"第 {line_num} 行: 使用默认样式 'solid'")
                style = "solid"
            
            # 返回解析后的参数
            return {
                "points": points,
                "color_id": color_id,
                "thickness": thickness,
                "style": style
            }
            
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params):
        """
        绘制路径
        
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
            points = params["points"]
            color_id = params["color_id"]
            thickness = params["thickness"]
            style = params["style"]
            
            # 获取颜色
            color = ColorSyntax.get_color(color_id)
            if not color:
                return False, image_array, width, height
            
            # 提取颜色
            r, g, b, a = color
            
            # 根据线条样式绘制路径
            if style == "solid":
                self._draw_solid_path(image_array, width, height, points, r, g, b, a, thickness)
            elif style == "dashed":
                self._draw_dashed_path(image_array, width, height, points, r, g, b, a, thickness)
            elif style == "wave":
                self._draw_wave_path(image_array, width, height, points, r, g, b, a, thickness)
            
            logger.info(f"已绘制路径，样式: {style}, 厚度: {thickness}, 点数: {len(points)}")
            
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"绘制路径时出错: {str(e)}")
            return False, image_array, width, height
    
    def _draw_solid_path(self, image_array, width, height, points, r, g, b, a, thickness):
        """绘制实线路径"""
        # 对每条线段进行绘制
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # 绘制线段
            self._draw_line(image_array, width, height, x1, y1, x2, y2, r, g, b, a, thickness)
    
    def _draw_dashed_path(self, image_array, width, height, points, r, g, b, a, thickness):
        """绘制虚线路径"""
        dash_length = max(3, thickness * 2)  # 短划线长度
        gap_length = max(2, thickness)       # 间隙长度
        
        # 对每条线段进行绘制
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # 计算线段长度
            length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            
            if length == 0:
                continue
            
            # 计算单位向量
            dx = (x2 - x1) / length
            dy = (y2 - y1) / length
            
            # 计算总的短划线和间隙数量
            total_segments = int(length / (dash_length + gap_length))
            
            # 绘制虚线
            for j in range(total_segments):
                # 短划线起点
                dash_start_x = x1 + (dash_length + gap_length) * j * dx
                dash_start_y = y1 + (dash_length + gap_length) * j * dy
                
                # 短划线终点
                dash_end_x = dash_start_x + dash_length * dx
                dash_end_y = dash_start_y + dash_length * dy
                
                # 确保不超出线段终点
                if j == total_segments - 1:
                    dash_end_x = min(dash_end_x, x2) if x2 > x1 else max(dash_end_x, x2)
                    dash_end_y = min(dash_end_y, y2) if y2 > y1 else max(dash_end_y, y2)
                
                # 绘制短划线
                self._draw_line(image_array, width, height, 
                               int(dash_start_x), int(dash_start_y), 
                               int(dash_end_x), int(dash_end_y), 
                               r, g, b, a, thickness)
    
    def _draw_wave_path(self, image_array, width, height, points, r, g, b, a, thickness):
        """绘制波浪线路径"""
        wave_height = max(2, thickness)  # 波浪振幅
        wave_length = max(4, thickness * 3)  # 波浪周期
        
        # 对每条线段进行绘制
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            
            # 计算线段长度
            length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            
            if length == 0:
                continue
            
            # 计算单位向量
            dx = (x2 - x1) / length
            dy = (y2 - y1) / length
            
            # 计算垂直向量
            nx = -dy
            ny = dx
            
            # 计算波浪点
            wave_points = []
            
            # 采样点数量，确保波浪平滑
            num_points = max(20, int(length / 2))
            
            for j in range(num_points + 1):
                # 计算波浪的振荡因子
                t = j / num_points
                wave_factor = wave_height * math.sin(t * length * 2 * math.pi / wave_length)
                
                # 计算波浪点坐标
                wave_x = x1 + t * (x2 - x1) + wave_factor * nx
                wave_y = y1 + t * (y2 - y1) + wave_factor * ny
                
                wave_points.append((wave_x, wave_y))
            
            # 绘制波浪线（连接波浪点）
            for j in range(len(wave_points) - 1):
                wx1, wy1 = wave_points[j]
                wx2, wy2 = wave_points[j + 1]
                
                self._draw_line(image_array, width, height, 
                               int(wx1), int(wy1), 
                               int(wx2), int(wy2), 
                               r, g, b, a, thickness)
    
    def _draw_line(self, image_array, width, height, x1, y1, x2, y2, r, g, b, a, thickness):
        """
        使用Bresenham算法绘制线段
        
        Args:
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            x1, y1: 起点坐标
            x2, y2: 终点坐标
            r, g, b, a: 颜色值
            thickness: 线条粗细
        """
        # 确保坐标在图像范围内
        def clip_point(x, y):
            return (
                max(0, min(width - 1, x)),
                max(0, min(height - 1, y))
            )
        
        # 如果线段完全在图像范围外，直接返回
        if ((x1 < 0 and x2 < 0) or (x1 >= width and x2 >= width) or
            (y1 < 0 and y2 < 0) or (y1 >= height and y2 >= height)):
            return
        
        # 裁剪坐标
        x1, y1 = clip_point(x1, y1)
        x2, y2 = clip_point(x2, y2)
        
        # 计算线段长度
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        # 确定绘制方向
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        # 初始误差
        err = dx - dy
        
        # Bresenham算法
        while True:
            # 绘制粗线（考虑thickness）
            if thickness == 1:
                # 单像素线条
                self._blend_pixel(image_array, x1, y1, r, g, b, a)
            else:
                # 粗线条（通过绘制圆形点）
                radius = thickness // 2
                for y in range(max(0, y1 - radius), min(height, y1 + radius + 1)):
                    for x in range(max(0, x1 - radius), min(width, x1 + radius + 1)):
                        # 计算到中心的距离
                        dist = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
                        if dist <= radius:
                            self._blend_pixel(image_array, x, y, r, g, b, a)
            
            # 到达终点，结束绘制
            if x1 == x2 and y1 == y2:
                break
            
            # 计算下一个像素位置
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy 