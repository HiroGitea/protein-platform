<script lang="ts">
	import { Dna, Search, Atom, Users, Database, Cpu, Beaker, Microscope } from 'lucide-svelte';
	
	const features = [
		{
			title: 'OpenFold',
			description: '基于深度学习的蛋白质结构预测工具，提供高精度的三维结构预测',
			icon: Dna,
			href: '/openfold',
			color: 'bg-blue-500'
		},
		{
			title: 'MMseqs2',
			description: '快速序列搜索和聚类工具，支持大规模蛋白质序列分析',
			icon: Search,
			href: '/mmseq',
			color: 'bg-green-500'
		},
		{
			title: 'DiffDock',
			description: '分子对接预测工具，用于药物发现和分子相互作用研究',
			icon: Atom,
			href: '/diffdock',
			color: 'bg-purple-500'
		},
		{
			title: '分子可视化',
			description: '基于Mol*的3D分子结构可视化工具，支持蛋白质和配体的交互式展示',
			icon: Atom,
			href: '/molviewer',
			color: 'bg-orange-500'
		},
		{
			title: 'GenMol',
			description: '基于离散扩散的通用分子生成模型，支持从头生成和片段约束生成',
			icon: Beaker,
			href: '/genmol',
			color: 'bg-blue-600'
		},
		{
			title: 'MolMIM',
			description: '基于生成式AI的分子优化平台，用于生成具有特定性质的分子',
			icon: Microscope,
			href: '/molmim',
			color: 'bg-purple-600'
		}
	];
	
	const stats = [
		{ label: '注册用户', value: '34', icon: Users },
		{ label: '分析任务', value: '5,678', icon: Database },
		{ label: '计算时长', value: '2,345h', icon: Cpu }
	];
</script>

<svelte:head>
	<title>生物信息学平台 - 首页</title>
	<meta name="description" content="集成多种生物信息学工具的综合平台" />
</svelte:head>

<div class="max-w-7xl mx-auto">
	<!-- 欢迎横幅 -->
	<div class="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg p-8 mb-8 text-white">
		<h1 class="text-4xl font-bold mb-4">欢迎使用生物信息学平台</h1>
		<p class="text-xl opacity-90 mb-6">
			集成OpenFold、MMseqs2、DiffDock、GenMol、MolMIM等先进工具，为您的生物信息学研究和药物发现提供强大支持
		</p>
		<div class="flex flex-wrap gap-4">
			<a href="/login" class="btn bg-white text-primary-600 hover:bg-gray-100">
				立即开始
			</a>
			<a href="/register" class="btn border-2 border-white text-white hover:bg-white hover:text-primary-600">
				注册账户
			</a>
		</div>
	</div>

	<!-- 统计数据 -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
		{#each stats as stat}
			<div class="card text-center">
				<div class="flex justify-center mb-4">
					<div class="p-3 bg-primary-100 dark:bg-primary-900 rounded-full">
						<svelte:component this={stat.icon} class="w-8 h-8 text-primary-600 dark:text-primary-400" />
					</div>
				</div>
				<div class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
					{stat.value}
				</div>
				<div class="text-gray-600 dark:text-gray-400">
					{stat.label}
				</div>
			</div>
		{/each}
	</div>

	<!-- 功能模块 -->
	<div class="mb-8">
		<h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-6 text-center">
			核心功能
		</h2>
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each features as feature}
				<a href={feature.href} class="card hover:shadow-xl transition-shadow group">
					<div class="flex items-center mb-4">
						<div class="p-3 {feature.color} rounded-lg mr-4">
							<svelte:component this={feature.icon} class="w-8 h-8 text-white" />
						</div>
						<h3 class="text-xl font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
							{feature.title}
						</h3>
					</div>
					<p class="text-gray-600 dark:text-gray-400 leading-relaxed">
						{feature.description}
					</p>
				</a>
			{/each}
		</div>
	</div>

	<!-- 快速开始指南 -->
	<div class="card">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
			快速开始
		</h2>
		<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
			<div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
					新用户
				</h3>
				<ol class="space-y-2 text-gray-600 dark:text-gray-400">
					<li class="flex items-center">
						<span class="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">1</span>
						注册账户并验证邮箱
					</li>
					<li class="flex items-center">
						<span class="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">2</span>
						选择需要使用的工具
					</li>
					<li class="flex items-center">
						<span class="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">3</span>
						上传数据并开始分析
					</li>
				</ol>
			</div>
			<div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">
					已有账户
				</h3>
				<ol class="space-y-2 text-gray-600 dark:text-gray-400">
					<li class="flex items-center">
						<span class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">1</span>
						登录您的账户
					</li>
					<li class="flex items-center">
						<span class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">2</span>
						查看历史分析结果
					</li>
					<li class="flex items-center">
						<span class="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">3</span>
						开始新的分析任务
					</li>
				</ol>
			</div>
		</div>
	</div>
</div> 