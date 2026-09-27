# frontend

生物信息学平台的前端：SvelteKit + TailwindCSS + Mol*。

完整项目说明见[仓库根目录 README](../README.md)。

## 跑起来

```bash
npm install
cp .env.example .env     # 配置后端地址，默认 http://127.0.0.1:8000
npm run dev
```

打开 http://localhost:5173。

后端没启动时，页面能打开，但所有需要计算的功能会提示连不上后端。

## 目录结构

```
src/
├── lib/
│   ├── api/
│   │   ├── client.ts            后端 API 客户端（提交任务 / 轮询 / 上传 / 下载）
│   │   └── types.ts             与 backend/app/schemas.py 一一对应
│   ├── components/
│   │   └── MoleculeViewer.svelte  Mol* 封装
│   └── utils/
│       └── molstar-loader.ts    Mol* 资源加载
└── routes/
    ├── +layout.svelte           侧边栏导航
    ├── +page.svelte             首页
    ├── molviewer/               分子可视化（已完成）
    ├── genmol/                  分子生成
    ├── molmim/                  分子优化
    ├── diffdock/                分子对接
    ├── mmseq/                   序列搜索
    ├── openfold/                结构预测
    ├── login/  register/        认证页面（占位）
    └── ...
```

## 页面状态

| 页面 | 状态 |
|---|---|
| `/molviewer` | ✅ 完整可用，真实 Mol* 集成 |
| `/genmol` `/molmim` `/diffdock` `/mmseq` `/openfold` | ⚠️ UI 完成，**仍在用 mock 数据**，待接入后端 |
| `/login` `/register` | ⚠️ 硬编码校验，无状态保存，待接入真实认证 |

> 那些 mock 是这个项目要解决的问题本身，不是特性。接后端时逐个删掉。

## 与后端对接

所有推理都是异步任务，`$lib/api/client.ts` 已封装：

```ts
import { generateMolecules, ApiError } from '$lib/api/client';

try {
  const result = await generateMolecules(
    { mode: 'denovo', num_samples: 10 },
    (job) => { progress = job.progress; message = job.message; }
  );
} catch (e) {
  if (e instanceof ApiError) error = e.message;
}
```

改了后端的 `schemas.py` 记得同步 `src/lib/api/types.ts`。

## 分子可视化

支持 PDB / CIF 蛋白质文件和 SDF / MOL / MOL2 配体文件，可同屏显示。
`static/examples/` 下有真实的 DiffDock 对接结果作为示例数据。

Mol* 的静态资源由 `copy-molstar-assets.js` 在 `dev` / `build` 时自动从
`node_modules` 复制到 `static/vendor/`（该目录不进版本库）。

## 常用命令

```bash
npm run dev       # 开发
npm run build     # 构建
npm run check     # svelte-check 类型检查
npm run lint      # prettier + eslint
npm run format    # 格式化
```
