# Computer Graphics Lab: Ray Casting, Phong Shading & Shadows

[![Taichi](https://img.shields.io/badge/Language-Taichi-blue.svg)](https://www.taichi-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

本实验基于 **Taichi** 高性能计算框架，实现了三维场景的 GPU 光线投射（Ray Casting）引擎。项目重点探究了光照模型（Phong vs Blinn-Phong）的视觉差异，并成功引入了硬阴影技术与参数交互调节界面。

##🚀 项目概览

* 核心功能：利用数学隐式方程在 GPU 上并行渲染三维场景。

* 技术栈：Python 3.12, Taichi Lang。

* 光照模型：支持切换至 Blinn-Phong，包含漫反射（Diffuse）、环境光（Ambient）及镜面高光（Specular）。

* 特殊效果：基于暗影射线（Shadow Ray）的硬阴影计算，解决了阴影粉刺（Shadow Acne）问题。

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
