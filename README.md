# 🎮 像素图像生成器 (Pixel Image Generator)

> 🌟 一个强大的像素艺术生成工具，使用简单的文本描述语法创建各种图像效果。
> 
> 🌟 A powerful pixel art generation tool that creates various image effects using simple text-based syntax.

<div align="center">
  <img src="https://img.shields.io/badge/版本-3.0.0-blue" alt="版本"/>
  <img src="https://img.shields.io/badge/Python-3.6+-brightgreen" alt="Python版本"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="许可证"/>
</div>

---

## ✨ 功能特性 (Features)

- 🎨 **简单易用的语法系统**，无需编程知识
- 🌈 **支持多种绘图方式**，满足各种创意需求
- 🔄 **高级功能**：循环、条件判断、区域变换等
- 📊 **丰富的效果**：可创建渐变、图案和复杂的几何结构
- 🖼️ **高质量输出**：生成清晰精美的PNG图像
- 🔍 **批量处理**：支持自动扫描处理input目录下的所有配置文件
- 📝 **详细报告**：生成完整的处理报告，方便追踪和优化
- 📊 **美观界面**：支持彩色化终端输出和动态进度显示

*English:*
- 🎨 **Simple and easy-to-use syntax system**, no programming knowledge required
- 🌈 **Supports various drawing methods** to meet different creative needs
- 🔄 **Advanced features**: Loops, conditionals, region transformations, etc.
- 📊 **Rich effects**: Create gradients, patterns, and complex geometric structures
- 🖼️ **High-quality output**: Generate clear and beautiful PNG images
- 🔍 **Batch processing**: Automatically scan and process all configuration files in the input directory
- 📝 **Detailed reports**: Generate complete processing reports for tracking and optimization
- 📊 **Beautiful interface**: Support for colorized terminal output and dynamic progress display

---

## 📥 安装指南 (Installation Guide)

### 📋 环境要求 (Requirements)
- Python 3.6+
- 所需依赖库：见requirements.txt
- Required libraries: See requirements.txt

### 🔧 安装步骤 (Installation Steps)

1️⃣ **克隆或下载本项目到本地** (Clone or download this project locally)
   ```bash
   git clone https://github.com/chsjkfqwjk/pixel_image_generator.git
   cd pixel_image_generator
   ```

2️⃣ **安装依赖** (Install dependencies)
   ```bash
   pip install -r requirements.txt
   ```

3️⃣ **运行程序** (Run the program)
   ```bash
   python pixel_image_generator.py
   ```

---

## 📚 使用说明 (Usage Instructions)

程序提供友好的交互式菜单界面，你可以：

1️⃣ 将配置文件（.txt格式）放入`input`目录
2️⃣ 运行程序并选择选项1"处理input目录中的所有文件"
3️⃣ 生成的图像将保存在`output`目录中
4️⃣ 处理报告会生成在output目录下的`processing_report.txt`文件中

*English:*
The program provides a friendly interactive menu interface where you can:

1️⃣ Place configuration files (.txt format) in the `input` directory
2️⃣ Run the program and select option 1 "Process all files in the input directory"
3️⃣ Generated images will be saved in the `output` directory
4️⃣ Processing reports will be generated in the `processing_report.txt` file in the output directory

---

## 🚀 高级语法功能 (Advanced Syntax Features)

像素图像生成器支持多种高级语法功能：

- ⚙️ **条件语句**：`if:条件表达式;指令1,指令2,...`
- 🔁 **循环语句**：`loop:变量\起始值\结束值\步长;指令1,指令2,...`
- 🧮 **表达式计算**：`{width/2}` `{x+y*10}` `{i%2==0?100:200}`
- 🌈 **渐变填充**：`gradient:区域ID\类型\起点x|y\终点x|y\起始颜色\结束颜色`

*English:*
The Pixel Image Generator supports various advanced syntax features:

- ⚙️ **Conditional statements**: `if:condition;instruction1,instruction2,...`
- 🔁 **Loop statements**: `loop:variable\start\end\step;instruction1,instruction2,...`
- 🧮 **Expression calculation**: `{width/2}` `{x+y*10}` `{i%2==0?100:200}`
- 🌈 **Gradient fill**: `gradient:regionID\type\startx|y\endx|y\startColor\endColor`

> 💡 更多语法细节，可以在程序中选择"语法详解与示例"选项查看。
> 
> 💡 For more syntax details, you can view the "Syntax explanation and examples" option in the program.

---

## 🤖 使用AI生成语法文件 (Using AI to Generate Syntax Files)

不熟悉语法？没关系！您可以直接向AI（如ChatGPT、Claude等）提交本项目的syntax.txt语法详解，然后描述您想要的图像效果，让AI为您生成语法文件。

Not familiar with the syntax? No problem! You can directly submit the syntax.txt reference from this project to AI (such as ChatGPT, Claude, etc.), then describe the image effect you want, and let AI generate the syntax file for you.

### 📝 示例提示词 (Example Prompt)

```
请帮我生成一个像素图像生成器的语法文件，要求：
1. 图像尺寸为800x600，白色背景
2. 在中心位置绘制一个红色五角星
3. 在四个角各绘制一个蓝色小圆形
4. 使用渐变色（从绿色到黄色）绘制一个横跨底部的长条

Please help me generate a syntax file for the pixel image generator with the following requirements:
1. Image size of 800x600 with a white background
2. Draw a red five-pointed star in the center
3. Draw a small blue circle in each of the four corners
4. Draw a horizontal bar across the bottom with a gradient from green to yellow
```
### 💡 提示技巧 (Tips)

为获得最佳结果，在向AI描述时：

1. **明确指定尺寸和背景色** - 确保图像基础设置清晰
2. **详细描述每个图形元素的位置、大小和颜色** - 提供准确的坐标和属性
3. **说明是否需要特殊效果（渐变、点阵等）** - 指定特殊视觉效果的参数
4. **如需条件逻辑或循环，请清晰说明逻辑规则** - 确保AI理解复杂的生成逻辑

*English:*
For best results when describing to AI:

1. **Clearly specify dimensions and background color** - Ensure image basic settings are clear
2. **Describe in detail the position, size, and color of each graphic element** - Provide accurate coordinates and attributes
3. **Specify if special effects are needed (gradients, dot patterns, etc.)** - Specify parameters for special visual effects
4. **For conditional logic or loops, clearly explain the logical rules** - Ensure AI understands complex generation logic

> 📌 将AI生成的语法保存为.txt文件，放入input目录，然后使用像素图像生成器处理即可。
> 
> 📌 Save the AI-generated syntax as a .txt file, place it in the input directory, and then process it with the Pixel Image Generator.

## 🤝 贡献指南 (Contribution Guidelines)

欢迎为像素图像生成器项目做出贡献：

Welcome to contribute to the Pixel Image Generator project:

1. 🍴 **Fork 本仓库** (Fork this repository)
2. 🌿 **创建新的功能分支** (`git checkout -b feature/amazing-feature`)
3. 💾 **提交更改** (`git commit -m '添加了一些功能'`)
4. 📤 **推送到分支** (`git push origin feature/amazing-feature`)
5. 🎁 **创建 Pull Request**

---

## 📜 许可证 (License)

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---

## 📬 联系方式 (Contact Information)

如有问题或建议，请通过以下方式联系：

For questions or suggestions, please contact through:

- 🌐 **项目地址 (Project Address)**：https://github.com/chsjkfqwjk/pixel_image_generator
- 📧 **电子邮件 (Email)**：q15052129276@163.com或3527008960@qq.com

---

## 💖 支持一下我 (Support Me)

如果您觉得这个项目对您有帮助，可以考虑通过以下方式支持我：

If you find this project helpful, you can consider supporting me through the following methods:

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="image/微信收款码.png" alt="微信支付 (WeChat Pay)" width="200"/>
        <p><small>扫码支付<br/>Scan QR code to pay</small></p>
      </td>
      <td align="center">
        <img src="image/支付宝收款码.jpg" alt="支付宝支付 (Alipay)" width="200"/>
        <p><small>扫码支付<br/>Scan QR code to pay</small></p>
      </td>
      <td align="center">
        <a href="https://paypal.me/chy2025?country.x=C2&locale.x=en_US">
          <img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_111x69.jpg" alt="PayPal" width="200"/>
        </a>
        <p><small>点击图片跳转至支付页面<br/>Click image to navigate to payment page</small></p>
      </td>
    </tr>
  </table>
</div>
