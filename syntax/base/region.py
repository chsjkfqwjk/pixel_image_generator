from .base import PixelSyntax, logger
import numpy as np
import json
import re

class RegionSyntax(PixelSyntax):
    """区域定义语法类，用于定义可重用的绘制区域"""
    
    # 区域字典，全局共享
    region_registry = {}
    
    # 预定义形状列表
    VALID_SHAPES = [
        "rect", "ellipse", "triangle", "diamond", "pentagon", 
        "hexagon", "star", "cross", "arrow"
    ]
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "region"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - id: 区域的唯一标识符
                - position1: 左上角坐标，格式为 "x1|y1"
                - position2: 右下角坐标，格式为 "x2|y2"
                - shape: 区域形状（可选，默认为rect）
                  支持的形状:
                  - rect: 矩形
                  - ellipse: 椭圆形
                  - triangle: 三角形（等边三角形）
                  - diamond: 菱形
                  - pentagon: 五边形
                  - hexagon: 六边形
                  - star: 五角星
                  - cross: 十字形
                  - arrow: 箭头
                  - "x1|y1-x2|y2-x3|y3...": 自定义多边形 - 直接使用坐标对定义，使用连字符'-'分隔点
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) < 3 or len(params) > 4:
            logger.warning(f"第 {line_num} 行: region语法需要3或4个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            region_id = str(params[0])
            pos1 = str(params[1])
            pos2 = str(params[2])
            
            # 检查坐标格式
            if '|' not in pos1 or '|' not in pos2:
                logger.warning(f"第 {line_num} 行: 坐标格式不正确，需要使用'|'分隔x和y坐标")
                return None
                
            # 解析坐标
            try:
                x1_str, y1_str = pos1.split('|', 1)
                x2_str, y2_str = pos2.split('|', 1)
                
                # 尝试转换为整数
                try:
                    x1 = int(x1_str)
                    y1 = int(y1_str)
                    x2 = int(x2_str)
                    y2 = int(y2_str)
                except ValueError:
                    # 如果转换为整数失败，尝试浮点数然后取整
                    try:
                        x1 = int(float(x1_str))
                        y1 = int(float(y1_str))
                        x2 = int(float(x2_str))
                        y2 = int(float(y2_str))
                    except ValueError as e:
                        logger.warning(f"第 {line_num} 行: 坐标必须为数值: {str(e)}")
                        return None
            except Exception as e:
                logger.warning(f"第 {line_num} 行: 坐标解析错误: {str(e)}")
                return None
            
            shape = "rect" if len(params) < 4 else str(params[3]).lower()
            
            # 验证参数
            if not region_id:
                logger.warning(f"第 {line_num} 行: 区域ID不能为空")
                return None
                
            # 确保x1 <= x2, y1 <= y2
            if x1 > x2:
                x1, x2 = x2, x1
                logger.info(f"第 {line_num} 行: 交换X坐标以确保x1 <= x2: ({x1},{x2})")
                
            if y1 > y2:
                y1, y2 = y2, y1
                logger.info(f"第 {line_num} 行: 交换Y坐标以确保y1 <= y2: ({y1},{y2})")
            
            # 检查是否为自定义形状（包含 '-' 和 '|'）
            custom_points = None
            is_custom_shape = False
            
            if '-' in shape and '|' in shape:
                try:
                    # 这是一个自定义形状坐标字符串
                    is_custom_shape = True
                    custom_points = self._parse_custom_points(shape, region_width=x2-x1+1, region_height=y2-y1+1)
                    if not custom_points or len(custom_points) < 3:
                        logger.warning(f"第 {line_num} 行: 自定义形状需要至少3个有效点")
                        return None
                    shape = "custom"  # 内部使用custom标识
                except Exception as e:
                    logger.warning(f"第 {line_num} 行: 自定义形状解析错误: {str(e)}")
                    return None
            elif shape not in self.VALID_SHAPES:
                logger.warning(f"第 {line_num} 行: 不支持的形状类型 '{shape}'，有效值: {self.VALID_SHAPES} 或 'x1|y1-x2|y2-x3|y3'格式的自定义多边形")
                logger.info(f"第 {line_num} 行: 使用默认形状 'rect'")
                shape = "rect"
            
            # 返回解析后的参数
            result = {
                "id": region_id,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "shape": shape
            }
            
            if custom_points:
                result["custom_points"] = custom_points
                
            return result
            
        except Exception as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def _parse_custom_points(self, points_str, region_width, region_height):
        """解析自定义形状的点坐标
        
        支持以下格式:
        - 坐标对格式: "x1|y1-x2|y2-x3|y3"，使用连字符'-'分隔点，使用竖线'|'分隔坐标
        - 支持相对坐标（0-1之间）或绝对坐标

        返回规范化后的点列表 [(x1,y1), (x2,y2), ...] 其中坐标都是相对区域左上角的绝对像素位置
        """
        points = []
        
        # 使用连字符分隔的坐标对格式（x1|y1-x2|y2-x3|y3）
        for point in points_str.split('-'):
            if '|' not in point:
                continue
                
            try:
                x_str, y_str = point.split('|', 1)
                x = float(x_str.strip())
                y = float(y_str.strip())
                
                # 判断是相对坐标还是绝对坐标
                if 0 <= x <= 1 and 0 <= y <= 1 and ('.' in x_str or '.' in y_str):
                    # 相对坐标，转换为绝对坐标
                    points.append((int(x * region_width), int(y * region_height)))
                else:
                    # 绝对坐标
                    points.append((int(x), int(y)))
            except:
                continue
                
        return points
    
    def apply(self, image_array, width, height, params):
        """
        注册区域到全局区域注册表
        
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
            region_id = params["id"]
            x1 = params["x1"]
            y1 = params["y1"]
            x2 = params["x2"]
            y2 = params["y2"]
            shape = params["shape"]
            custom_points = params.get("custom_points")
            
            # 校正坐标（确保在图像范围内）
            x1 = max(0, min(width - 1, x1))
            y1 = max(0, min(height - 1, y1))
            x2 = max(0, min(width - 1, x2))
            y2 = max(0, min(height - 1, y2))
            
            # 创建区域掩码
            region_width = x2 - x1 + 1
            region_height = y2 - y1 + 1
            
            # 如果尺寸无效，返回错误
            if region_width <= 0 or region_height <= 0:
                logger.warning(f"区域 {region_id} 尺寸无效: {region_width}x{region_height}")
                return False, image_array, width, height
            
            # 创建掩码
            mask = np.zeros((region_height, region_width), dtype=bool)
            
            # 根据形状设置掩码
            if shape == "rect":
                # 矩形区域（全部为True）
                mask[:, :] = True
                
            elif shape == "ellipse":
                # 椭圆区域
                center_y, center_x = region_height // 2, region_width // 2
                radius_y, radius_x = region_height / 2, region_width / 2
                
                y_coords, x_coords = np.ogrid[:region_height, :region_width]
                
                # 椭圆方程: (x-h)²/a² + (y-k)²/b² <= 1
                dist_from_center = ((x_coords - center_x) / radius_x) ** 2 + ((y_coords - center_y) / radius_y) ** 2
                mask = dist_from_center <= 1.0
                
            elif shape == "triangle":
                # 等边三角形，底边平行于x轴，顶点向上
                y_coords, x_coords = np.ogrid[:region_height, :region_width]
                
                # 定义三角形的三个点
                p1 = (region_width//2, 0)  # 顶点
                p2 = (0, region_height-1)  # 左下角
                p3 = (region_width-1, region_height-1)  # 右下角
                
                mask = self._polygon_mask(region_width, region_height, [p1, p2, p3])
                
            elif shape == "diamond":
                # 菱形区域（正方形旋转45度）
                center_y, center_x = region_height // 2, region_width // 2
                
                # 菱形的四个顶点
                p1 = (center_x, 0)  # 上
                p2 = (region_width-1, center_y)  # 右
                p3 = (center_x, region_height-1)  # 下
                p4 = (0, center_y)  # 左
                
                mask = self._polygon_mask(region_width, region_height, [p1, p2, p3, p4])
                
            elif shape == "pentagon":
                # 五边形（正五边形）
                center_y, center_x = region_height // 2, region_width // 2
                radius = min(center_x, center_y)
                
                # 计算正五边形的五个顶点
                points = []
                for i in range(5):
                    angle = 2 * np.pi * i / 5 - np.pi/2  # 从顶部开始
                    x = center_x + int(radius * np.cos(angle))
                    y = center_y + int(radius * np.sin(angle))
                    points.append((x, y))
                
                mask = self._polygon_mask(region_width, region_height, points)
                
            elif shape == "hexagon":
                # 六边形（正六边形）
                center_y, center_x = region_height // 2, region_width // 2
                radius = min(center_x, center_y)
                
                # 计算正六边形的六个顶点
                points = []
                for i in range(6):
                    angle = 2 * np.pi * i / 6
                    x = center_x + int(radius * np.cos(angle))
                    y = center_y + int(radius * np.sin(angle))
                    points.append((x, y))
                
                mask = self._polygon_mask(region_width, region_height, points)
                
            elif shape == "star":
                # 五角星
                center_y, center_x = region_height // 2, region_width // 2
                outer_radius = min(center_x, center_y)
                inner_radius = outer_radius * 0.4  # 内部星点的半径
                
                # 计算五角星的10个顶点（5个外顶点和5个内顶点交替）
                points = []
                for i in range(10):
                    # 确定这是外顶点还是内顶点
                    radius = outer_radius if i % 2 == 0 else inner_radius
                    angle = 2 * np.pi * (i / 10) - np.pi/2  # 从顶部开始
                    x = center_x + int(radius * np.cos(angle))
                    y = center_y + int(radius * np.sin(angle))
                    points.append((x, y))
                
                mask = self._polygon_mask(region_width, region_height, points)
                
            elif shape == "cross":
                # 十字形
                center_y, center_x = region_height // 2, region_width // 2
                arm_width = min(region_width, region_height) // 3
                
                # 水平部分
                mask[center_y-arm_width//2:center_y+arm_width//2+1, :] = True
                # 垂直部分
                mask[:, center_x-arm_width//2:center_x+arm_width//2+1] = True
                
            elif shape == "arrow":
                # 箭头（向右）
                center_y = region_height // 2
                arrow_head_width = region_height // 2
                shaft_width = region_height // 4
                
                # 箭头主体（矩形）
                mask[center_y-shaft_width:center_y+shaft_width, :region_width*2//3] = True
                
                # 箭头头部（三角形）
                head_start_x = region_width*2//3 - 1
                
                for y in range(region_height):
                    for x in range(head_start_x, region_width):
                        # 计算点到三角形边的距离
                        if abs(y - center_y) <= arrow_head_width * (1 - (x - head_start_x) / (region_width - head_start_x)):
                            mask[y, x] = True
                
            elif shape == "custom" and custom_points:
                # 自定义形状
                mask = self._polygon_mask(region_width, region_height, custom_points)
            
            # 注册区域
            RegionSyntax.region_registry[region_id] = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "shape": shape,
                "mask": mask
            }
            
            if shape == "custom" and custom_points:
                RegionSyntax.region_registry[region_id]["custom_points"] = custom_points
            
            shape_display = shape if shape != "custom" else "custom_polygon"
            logger.info(f"已定义区域: {region_id} = ({x1},{y1},{x2},{y2}), 形状: {shape_display}")
            
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"注册区域时出错: {str(e)}")
            return False, image_array, width, height
    
    def _point_in_polygon(self, x, y, polygon):
        """判断点(x,y)是否在多边形内部
        
        使用射线法（Ray Casting Algorithm）判断点是否在多边形内部
        """
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
    
    def _polygon_mask(self, width, height, points):
        """创建多边形掩码"""
        mask = np.zeros((height, width), dtype=bool)
        
        # 为每个点判断是否在多边形内部
        for y in range(height):
            for x in range(width):
                mask[y, x] = self._point_in_polygon(x, y, points)
                
        return mask
    
    @classmethod
    def get_region(cls, region_id):
        """
        获取已注册的区域
        
        Args:
            region_id: 区域标识符
            
        Returns:
            区域字典或None（如果未找到）
        """
        return cls.region_registry.get(region_id) 