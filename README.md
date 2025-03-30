# 像素图像生成器 (Pixel Image Generator)

一个强大的像素艺术生成工具，使用简单的文本描述语法创建各种图像效果。

## 功能特性

- 🎨 简单易用的语法系统，无需编程知识
- 🌈 支持多种绘图方式
- 🔄 支持高级功能：循环、条件判断、区域变换
- 📊 可以创建渐变、图案和复杂的几何结构
- 🖼️ 输出高质量PNG图像
- 🔍 支持自动扫描处理input目录下的所有配置文件
- 📝 生成详细的处理报告
- 📊 支持彩色化终端输出和进度显示

## 安装指南

### 环境要求
- Python 3.6+
- 所需依赖库：见requirements.txt

### 安装步骤

1. 克隆或下载本项目到本地
   ```bash
   git clone https://github.com/chsjkfqwjk/pixel_image_generator.git
   cd pixel_image_generator
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 运行程序
   ```bash
   python pixel_image_generator.py
   ```

## 使用说明

程序提供友好的交互式菜单界面，你可以：

1. 将配置文件（.txt格式）放入`input`目录
2. 运行程序并选择选项1"处理input目录中的所有文件"
3. 生成的图像将保存在`output`目录中
4. 处理报告会生成在output目录下的`processing_report.txt`文件中

## 基本语法示例

像素图像生成器使用简单直观的语法来描述图像：

```
# 这是注释行

# 配置图像尺寸和背景色（白色背景）
config:400\300\255\255\255

# 定义颜色
color:blue\0\0\255       # 蓝色
color:red\255\0\0        # 红色

# 定义区域
region:box1\50|50\150|150           # 矩形区域
region:circle\200|50\300|150\ellipse  # 椭圆区域

# 填充区域
fill:box1\red      # 用红色填充第一个矩形
fill:circle\blue   # 用蓝色填充椭圆
```

## 高级语法功能

像素图像生成器支持多种高级语法功能：

- **条件语句**：`if:条件表达式;指令1,指令2,...`
- **循环语句**：`loop:变量\起始值\结束值\步长;指令1,指令2,...`
- **表达式计算**：`{width/2}` `{x+y*10}` `{i%2==0?100:200}`
- **渐变填充**：`gradient:区域ID\类型\起点x|y\终点x|y\起始颜色\结束颜色`

更多语法细节，可以在程序中选择"语法详解与示例"选项查看。

## 目录结构

```
pixel_image_generator/
├── pixel_image_generator.py  # 主程序
├── README.md                 # 说明文档
├── requirements.txt          # 依赖库清单
├── input/                    # 输入文件目录
├── output/                   # 输出图像目录
└── logs/                     # 日志文件目录
```

## 贡献指南

欢迎为像素图像生成器项目做出贡献：

1. Fork 本仓库
2. 创建新的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加了一些功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目地址：https://github.com/yourusername/pixel_image_generator
- 电子邮件：your.email@example.com
