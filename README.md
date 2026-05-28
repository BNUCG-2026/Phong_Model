# Computer Graphics Lab: Ray Casting, Phong Shading & Shadows

[![Taichi](https://img.shields.io/badge/Language-Taichi-blue.svg)](https://www.taichi-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

本实验基于 **Taichi** 高性能计算框架，实现了三维场景的 GPU 光线投射（Ray Casting）引擎。项目重点探究了光照模型（Phong vs Blinn-Phong）的视觉差异，并成功引入了硬阴影技术与参数交互调节界面。

## 📸 实验效果演示

以下展示了通过实时调整 `Shininess` 与材质系数，以及物体间产生的实时阴影遮挡效果：

![交互参数调整与硬阴影展示](assets/demo.gif)

*演示说明：通过交互面板实时改变材质属性，观察高光形态的丝滑变化及遮挡产生的物理阴影。*

---

## 🛠️ 环境配置与运行

### 依赖环境
* Python 3.12+
* [Taichi](https://docs.taichi-lang.org/) (用于 GPU 并行渲染)

### 快速安装
```bash
# 使用 pip 安装
pip install taichi
