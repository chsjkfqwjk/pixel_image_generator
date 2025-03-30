# 🎮 像素图像生成器 (Pixel Image Generator)

> 🌟 一个强大的像素艺术生成工具，使用简单的文本描述语法创建各种图像效果。

<div align="center">
  <img src="https://img.shields.io/badge/版本-3.0.0-blue" alt="版本"/>
  <img src="https://img.shields.io/badge/Python-3.6+-brightgreen" alt="Python版本"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="许可证"/>
</div>

---

## ✨ 功能特性

- 🎨 **简单易用的语法系统**，无需编程知识
- 🌈 **支持多种绘图方式**，满足各种创意需求
- 🔄 **高级功能**：循环、条件判断、区域变换等
- 📊 **丰富的效果**：可创建渐变、图案和复杂的几何结构
- 🖼️ **高质量输出**：生成清晰精美的PNG图像
- 🔍 **批量处理**：支持自动扫描处理input目录下的所有配置文件
- 📝 **详细报告**：生成完整的处理报告，方便追踪和优化
- 📊 **美观界面**：支持彩色化终端输出和动态进度显示

---

## 📥 安装指南

### 📋 环境要求
- Python 3.6+
- 所需依赖库：见requirements.txt

### 🔧 安装步骤

1️⃣ **克隆或下载本项目到本地**
   ```bash
   git clone https://github.com/chsjkfqwjk/pixel_image_generator.git
   cd pixel_image_generator
   ```

2️⃣ **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3️⃣ **运行程序**
   ```bash
   python pixel_image_generator.py
   ```

---

## 📚 使用说明

程序提供友好的交互式菜单界面，你可以：

1️⃣ 将配置文件（.txt格式）放入`input`目录
2️⃣ 运行程序并选择选项1"处理input目录中的所有文件"
3️⃣ 生成的图像将保存在`output`目录中
4️⃣ 处理报告会生成在output目录下的`processing_report.txt`文件中

---

## 🎯 基本语法示例

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

---

## 🚀 高级语法功能

像素图像生成器支持多种高级语法功能：

- ⚙️ **条件语句**：`if:条件表达式;指令1,指令2,...`
- 🔁 **循环语句**：`loop:变量\起始值\结束值\步长;指令1,指令2,...`
- 🧮 **表达式计算**：`{width/2}` `{x+y*10}` `{i%2==0?100:200}`
- 🌈 **渐变填充**：`gradient:区域ID\类型\起点x|y\终点x|y\起始颜色\结束颜色`

> 💡 更多语法细节，可以在程序中选择"语法详解与示例"选项查看。

---

## 🤖 使用AI生成语法文件

不熟悉语法？没关系！您可以直接向AI（如ChatGPT、Claude等）描述您想要的图像效果，让AI为您生成语法文件。

### 📝 示例提示词

```
请帮我生成一个像素图像生成器的语法文件，要求：
1. 图像尺寸为800x600，白色背景
2. 在中心位置绘制一个红色五角星
3. 在四个角各绘制一个蓝色小圆形
4. 使用渐变色（从绿色到黄色）绘制一个横跨底部的长条
```

### ✅ AI生成的语法文件示例

```
# 配置图像尺寸和背景色
config:800\600\255\255\255

# 定义颜色
color:red\255\0\0
color:blue\0\0\255
color:green\0\255\0
color:yellow\255\255\0

# 定义中心五角星
region:center_star\350|250\450|350\star
fill:center_star\red

# 定义四个角的圆形
region:circle_tl\20|20\60|60\ellipse
region:circle_tr\740|20\780|60\ellipse
region:circle_bl\20|540\60\580\ellipse
region:circle_br\740|540\780\580\ellipse

# 填充圆形
fill:circle_tl\blue
fill:circle_tr\blue
fill:circle_bl\blue
fill:circle_br\blue

# 底部渐变长条
region:bottom_bar\0|550\800\600
gradient:bottom_bar\linear\0|550\800\600\green\yellow
```

### 💡 提示技巧

为获得最佳结果，在向AI描述时：

1. **明确指定尺寸和背景色** - 确保图像基础设置清晰
2. **详细描述每个图形元素的位置、大小和颜色** - 提供准确的坐标和属性
3. **说明是否需要特殊效果（渐变、点阵等）** - 指定特殊视觉效果的参数
4. **如需条件逻辑或循环，请清晰说明逻辑规则** - 确保AI理解复杂的生成逻辑

> 📌 将AI生成的语法保存为.txt文件，放入input目录，然后使用像素图像生成器处理即可。

---

## 📂 目录结构

```
pixel_image_generator/
├── pixel_image_generator.py  # 主程序
├── README.md                 # 说明文档
├── requirements.txt          # 依赖库清单
├── input/                    # 输入文件目录
├── output/                   # 输出图像目录
└── logs/                     # 日志文件目录
```

---

## 🤝 贡献指南

欢迎为像素图像生成器项目做出贡献：

1. 🍴 **Fork 本仓库**
2. 🌿 **创建新的功能分支** (`git checkout -b feature/amazing-feature`)
3. 💾 **提交更改** (`git commit -m '添加了一些功能'`)
4. 📤 **推送到分支** (`git push origin feature/amazing-feature`)
5. 🎁 **创建 Pull Request**

---

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📬 联系方式

如有问题或建议，请通过以下方式联系：

- 🌐 **项目地址**：https://github.com/chsjkfqwjk/pixel_image_generator
- 📧 **电子邮件**：q15052129276@163.com或3527008960@qq.com

---

## 💖 支持一下我

如果您觉得这个项目对您有帮助，可以考虑通过以下方式支持我：

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="image/微信收款码.png" alt="微信支付" width="300"/>
      </td>
      <td align="center">
        <img src="image/支付宝收款码.jpg" alt="支付宝支付" width="300"/>
      </td>
    </tr>
  </table>
</div>
