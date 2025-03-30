import numpy as np
import logging
from scipy import ndimage
from syntax.base.base import PixelSyntax
from syntax.base.region import RegionSyntax  # 直接导入RegionSyntax

# 获取日志记录器
logger = logging.getLogger('pixel_image_generator')

class TransformSyntax(PixelSyntax):
    """变换语法类，用于对区域进行变换操作"""
    
    @classmethod
    def get_name(cls):
        """获取语法名称"""
        return "transform"
    
    def parse_params(self, params, line_num=None):
        """
        解析参数列表
        
        Args:
            params: 包含以下参数的列表:
                - region_id: 要变换的区域ID
                - action: 变换动作（rotate、scale、translate、flip）
                - param: 变换参数（旋转角度、缩放因子、平移距离等）
                  对于translate: dx-dy格式
                  对于scale: x-y格式
                  对于flip: vertical或horizontal或both
                  对于rotate: 角度值
            line_num: 行号（用于日志）
        
        Returns:
            解析后的参数字典，或解析失败时返回None
        """
        if line_num is None:
            line_num = "?"
            
        # 检查参数数量
        if len(params) != 3:
            logger.warning(f"第 {line_num} 行: transform语法需要3个参数，实际提供了 {len(params)} 个")
            return None
            
        try:
            # 提取参数
            region_id = params[0].strip()
            action = params[1].strip().lower()
            param = params[2]
            
            # 验证参数
            if not region_id:
                logger.warning(f"第 {line_num} 行: 区域ID不能为空")
                return None
                
            # 检查操作类型
            valid_actions = ["rotate", "scale", "translate", "flip"]
            if action not in valid_actions:
                logger.warning(f"第 {line_num} 行: 不支持的变换操作 '{action}'，支持的操作有: {', '.join(valid_actions)}")
                return None
            
            # 解析参数（根据操作类型）
            parsed_param = self._parse_transform_param(action, param, line_num)
            if parsed_param is None:
                return None
            
            # 返回解析后的参数
            return {
                "region_id": region_id,
                "action": action,
                "param": parsed_param
            }
            
        except Exception as e:
            logger.warning(f"第 {line_num} 行: 参数解析错误: {str(e)}")
            return None
    
    def _parse_transform_param(self, action, param, line_num):
        """
        根据变换类型解析参数
        
        Args:
            action: 变换动作
            param: 变换参数
            line_num: 行号
            
        Returns:
            解析后的参数，或解析失败时返回None
        """
        try:
            if action == "rotate":
                # 旋转角度，单位为度
                angle = float(param)
                return angle
                
            elif action == "scale":
                # 缩放因子，可以是单个数字或x|y形式的两个数字
                if "|" in param:
                    parts = param.split("|")
                    if len(parts) != 2:
                        logger.warning(f"第 {line_num} 行: 缩放参数格式错误，应为'sx|sy'")
                        return None
                    sx = float(parts[0])
                    sy = float(parts[1])
                    return (sx, sy)
                else:
                    # 向后兼容处理：支持旧的"-"分隔符
                    if "-" in param:
                        parts = param.split("-")
                        if len(parts) != 2:
                            logger.warning(f"第 {line_num} 行: 缩放参数格式错误，应为'sx|sy'")
                            return None
                        sx = float(parts[0])
                        sy = float(parts[1])
                        return (sx, sy)
                    else:
                        scale = float(param)
                        return (scale, scale)  # 等比例缩放
                    
            elif action == "translate":
                # 平移距离，格式为'dx|dy'
                if "|" in param:
                    parts = param.split("|")
                    if len(parts) != 2:
                        logger.warning(f"第 {line_num} 行: 平移参数格式错误，应为'dx|dy'")
                        return None
                    dx = int(parts[0])
                    dy = int(parts[1])
                    return (dx, dy)
                else:
                    # 向后兼容处理：支持旧的"-"分隔符
                    if "-" in param:
                        parts = param.split("-")
                        if len(parts) != 2:
                            logger.warning(f"第 {line_num} 行: 平移参数格式错误，应为'dx|dy'")
                            return None
                        dx = int(parts[0])
                        dy = int(parts[1])
                        return (dx, dy)
                    else:
                        logger.warning(f"第 {line_num} 行: 平移参数格式错误，应为'dx|dy'")
                        return None
                
            elif action == "flip":
                # 翻转方向，vertical或horizontal或both
                direction = param.strip().lower()
                if direction not in ["vertical", "horizontal", "both"]:
                    logger.warning(f"第 {line_num} 行: 翻转方向错误，应为'vertical'、'horizontal'或'both'")
                    return None
                return direction
                
            else:
                logger.warning(f"第 {line_num} 行: 不支持的变换操作 '{action}'")
                return None
                
        except (ValueError, TypeError) as e:
            logger.warning(f"第 {line_num} 行: 变换参数解析错误: {str(e)}")
            return None
    
    def apply(self, image_array, width, height, params, region_manager=None):
        """
        应用变换操作
        
        Args:
            image_array: 图像数组
            width: 图像宽度
            height: 图像高度
            params: 已解析的参数
            region_manager: 区域管理器实例，用于获取区域信息
            
        Returns:
            True表示应用成功，False表示应用失败
        """
        try:
            region_id = params["region_id"]
            action = params["action"]
            param = params["param"]
            
            # 获取区域信息 - 直接从RegionSyntax获取区域
            logger.debug(f"正在查找区域: '{region_id}'")
            region_info = RegionSyntax.get_region(region_id)
            
            if region_info is None:
                logger.error(f"区域 '{region_id}' 未定义")
                # 尝试列出所有已定义的区域
                logger.debug(f"已定义的区域: {list(RegionSyntax.region_registry.keys())}")
                return False, image_array, width, height
                
            # 提取区域边界
            x1, y1, x2, y2 = region_info.get("x1"), region_info.get("y1"), region_info.get("x2"), region_info.get("y2")
            region_shape = region_info.get("shape", "rect")
            
            # 确保坐标有效
            if not all(isinstance(coord, (int, float)) for coord in [x1, y1, x2, y2]):
                logger.error(f"区域 '{region_id}' 坐标无效")
                return False, image_array, width, height
                
            # 提取区域图像
            region_width = int(x2 - x1)
            region_height = int(y2 - y1)
            region_image = np.copy(image_array[int(y1):int(y2), int(x1):int(x2)])
            
            # 创建区域掩码（用于透明度处理）
            if region_shape == "ellipse":
                mask = self._create_ellipse_mask(region_width, region_height)
            else:  # 默认为矩形
                mask = np.ones((region_height, region_width), dtype=bool)
            
            # 应用变换
            if action == "rotate":
                transformed_region, new_mask = self._apply_rotation(region_image, mask, param)
            elif action == "scale":
                transformed_region, new_mask = self._apply_scaling(region_image, mask, param, region_width, region_height)
            elif action == "translate":
                transformed_region, new_mask = self._apply_translation(region_image, mask, param, region_width, region_height)
            elif action == "flip":
                transformed_region, new_mask = self._apply_flip(region_image, mask, param)
            else:
                logger.error(f"不支持的变换操作 '{action}'")
                return False, image_array, width, height
            
            # 将变换后的区域放回原图像
            for y in range(region_height):
                for x in range(region_width):
                    if 0 <= y < new_mask.shape[0] and 0 <= x < new_mask.shape[1] and new_mask[y, x]:
                        img_y, img_x = int(y1) + y, int(x1) + x
                        if 0 <= img_y < height and 0 <= img_x < width:
                            if y < transformed_region.shape[0] and x < transformed_region.shape[1]:
                                image_array[img_y, img_x] = transformed_region[y, x]
            
            logger.info(f"已对区域 '{region_id}' 应用 {action} 变换")
            return True, image_array, width, height
            
        except Exception as e:
            logger.error(f"应用变换时出错: {str(e)}")
            return False, image_array, width, height
    
    def _create_ellipse_mask(self, width, height):
        """创建椭圆形掩码"""
        y, x = np.ogrid[:height, :width]
        center_x, center_y = width / 2, height / 2
        mask = ((x - center_x)**2 / (center_x**2) + (y - center_y)**2 / (center_y**2)) <= 1
        return mask
    
    def _apply_rotation(self, region_image, mask, angle):
        """
        应用旋转变换
        
        Args:
            region_image: 区域图像数组
            mask: 区域掩码
            angle: 旋转角度（度）
            
        Returns:
            变换后的区域图像和掩码
        """
        # 将掩码扩展到与图像相同的维度
        mask_3d = np.stack([mask] * 4, axis=2)
        
        # 旋转图像（使用最近邻插值以保持像素风格）
        rotated_image = ndimage.rotate(region_image, angle, reshape=False, order=0)
        
        # 同样旋转掩码
        rotated_mask = ndimage.rotate(mask, angle, reshape=False, order=0)
        
        return rotated_image, rotated_mask
    
    def _apply_scaling(self, region_image, mask, scale_factors, width, height):
        """
        应用缩放变换
        
        Args:
            region_image: 区域图像数组
            mask: 区域掩码
            scale_factors: 缩放因子(sx, sy)
            width: 区域宽度
            height: 区域高度
            
        Returns:
            变换后的区域图像和掩码
        """
        sx, sy = scale_factors
        
        # 计算目标尺寸
        target_width, target_height = int(width * sx), int(height * sy)
        
        # 缩放图像
        scaled_image = np.zeros((height, width, 4), dtype=np.uint8)
        scaled_mask = np.zeros((height, width), dtype=bool)
        
        if target_width > 0 and target_height > 0:
            # 使用最近邻插值进行缩放（保持像素风格）
            temp_image = ndimage.zoom(region_image, (sy, sx, 1), order=0)
            temp_mask = ndimage.zoom(mask, (sy, sx), order=0)
            
            # 确定放置位置（居中）
            x_offset = max(0, (width - target_width) // 2)
            y_offset = max(0, (height - target_height) // 2)
            
            # 放置缩放后的图像
            for y in range(min(target_height, height)):
                for x in range(min(target_width, width)):
                    if y < temp_mask.shape[0] and x < temp_mask.shape[1] and temp_mask[y, x]:
                        dest_y, dest_x = y_offset + y, x_offset + x
                        if 0 <= dest_y < height and 0 <= dest_x < width:
                            scaled_image[dest_y, dest_x] = temp_image[y, x]
                            scaled_mask[dest_y, dest_x] = True
        
        return scaled_image, scaled_mask
    
    def _apply_translation(self, region_image, mask, translation, width, height):
        """
        应用平移变换
        
        Args:
            region_image: 区域图像数组
            mask: 区域掩码
            translation: 平移量(dx, dy)
            width: 区域宽度
            height: 区域高度
            
        Returns:
            变换后的区域图像和掩码
        """
        dx, dy = translation
        
        # 创建新的图像和掩码
        translated_image = np.zeros_like(region_image)
        translated_mask = np.zeros_like(mask)
        
        # 对每个像素进行平移
        for y in range(height):
            for x in range(width):
                new_x, new_y = x + dx, y + dy
                if 0 <= new_y < height and 0 <= new_x < width and mask[y, x]:
                    translated_image[new_y, new_x] = region_image[y, x]
                    translated_mask[new_y, new_x] = True
        
        return translated_image, translated_mask
    
    def _apply_flip(self, region_image, mask, direction):
        """
        应用翻转变换
        
        Args:
            region_image: 区域图像数组
            mask: 区域掩码
            direction: 翻转方向（vertical、horizontal、both）
            
        Returns:
            变换后的区域图像和掩码
        """
        if direction == "vertical":
            flipped_image = np.flipud(region_image)
            flipped_mask = np.flipud(mask)
        elif direction == "horizontal":
            flipped_image = np.fliplr(region_image)
            flipped_mask = np.fliplr(mask)
        else:  # both
            flipped_image = np.flipud(np.fliplr(region_image))
            flipped_mask = np.flipud(np.fliplr(mask))
            
        return flipped_image, flipped_mask 