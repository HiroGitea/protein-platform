> 模型背景资料。平台各功能的**当前实现状态**以[根目录 README](../README.md)为准。

# GenMol 和 MolMIM 功能说明

本文档介绍了在生物信息学平台中新添加的两个分子生成和优化功能：GenMol 和 MolMIM。

## 🧪 GenMol - 分子生成模型

### 功能概述
GenMol是一个基于离散扩散的通用分子生成框架，能够处理多种药物发现场景。该模型使用SAFE（Sequential Attachment-based Fragment Embedding）序列表示，通过非自回归双向并行解码生成分子。

### 主要特性
- **从头分子生成**：无需输入分子即可生成全新的分子结构
- **片段约束生成**：基于给定的分子片段生成相关分子
- **目标导向优化**：生成具有特定性质的分子
- **先导化合物优化**：基于已知分子生成改进的类似物

### 技术优势
- 并行解码，效率更高
- 片段重掩蔽策略
- 分子上下文引导
- SAFE序列表示

### 使用方法
1. 访问 `/genmol` 页面
2. 输入SMILES（可选，用于引导生成）
3. 设置生成分子数量（1-100）
4. 调整温度参数控制多样性
5. 点击"开始生成"获取结果

## 🔬 MolMIM - 分子优化模型

### 功能概述
MolMIM是NVIDIA BioNeMo平台中的分子优化模型，专门用于生成具有特定性质的分子。该模型使用受控生成技术，在用户指定的Oracle函数指导下，浏览化学空间的学习内部表示。

### 核心功能
- **分子性质优化**：针对特定性质优化分子结构
- **多目标优化**：同时优化多个分子性质
- **受控分子生成**：在约束条件下生成分子
- **化学空间探索**：系统性地搜索化学空间

### 技术特点
- CMA-ES优化算法
- 潜在空间搜索
- 迭代优化过程
- Oracle函数引导

### 支持的性质
- **QED (药物相似性)**：评估分子的药物相似性
- **LogP (脂水分配系数)**：评估分子的亲脂性
- **SA (合成可达性)**：评估分子的合成难易程度
- **TPSA (极性表面积)**：评估分子的极性表面积

### 使用方法
1. 访问 `/molmim` 页面
2. 输入起始分子的SMILES
3. 选择要优化的目标性质
4. 设置优化步数（50-500）
5. 点击"开始优化"进行分子优化

## 🚀 应用场景

### GenMol 应用场景
- **药物发现**：生成具有特定性质的候选分子
- **先导优化**：基于已知分子生成类似物
- **化学空间探索**：发现新的化学结构

### MolMIM 应用场景
- **药物发现**：优化候选药物分子
- **先导化合物优化**：改进现有化合物的性质
- **分子设计**：设计具有特定功能的分子
- **性质预测**：预测和优化分子性质

## 📚 相关资源

### GenMol 资源
- [论文](https://arxiv.org/abs/2501.06158) - arXiv预印本
- [代码](https://github.com/NVIDIA/GenMol) - GitHub仓库
- [博客](https://developer.nvidia.com/zh-cn/blog/evaluating-genmol-as-a-generalist-foundation-model-for-molecular-generation/) - NVIDIA开发者博客

### MolMIM 资源
- [官方博客](https://developer.nvidia.com/zh-cn/blog/new-models-molmim-and-diffdock-power-molecule-generation-and-molecular-docking-in-bionemo/) - NVIDIA开发者
- [BioNeMo平台](https://www.nvidia.com/en-us/clara/bionemo/) - NVIDIA Clara
- [应用案例](https://blogs.nvidia.cn/blog/drug-discovery-bionemo-generative-ai/) - 药物研发

## 🛠️ 技术实现

### 前端实现
- 使用 Svelte/SvelteKit 框架
- Tailwind CSS 样式
- Lucide 图标库
- 响应式设计

### 页面结构
```
src/routes/
├── genmol/
│   └── +page.svelte    # GenMol 功能页面
├── molmim/
│   └── +page.svelte    # MolMIM 功能页面
└── +layout.svelte      # 更新的侧边栏导航
```

### 侧边栏更新
- 添加了 GenMol 和 MolMIM 导航链接
- 使用 Beaker 和 Microscope 图标
- 保持与现有设计的一致性

## 📝 注意事项

1. **模拟功能**：当前实现为演示版本，使用模拟数据和算法
2. **实际部署**：生产环境需要集成真实的GenMol和MolMIM模型
3. **性能优化**：大规模使用时需要考虑计算资源和响应时间
4. **数据验证**：需要添加输入数据的验证和错误处理

## 🔄 未来改进

1. **后端集成**：连接真实的模型API
2. **结果可视化**：添加分子结构的3D可视化
3. **批量处理**：支持批量分子生成和优化
4. **历史记录**：保存用户的分析历史
5. **导出功能**：支持多种格式的结果导出

---

*最后更新：2025年5月29日* 