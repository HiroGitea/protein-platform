<script lang="ts">
	import { Microscope, Target, Play, Download, FileText, ExternalLink, TrendingUp } from 'lucide-svelte';
	
	let inputSmiles = 'CCO';
	let targetProperty = 'QED';
	let optimizationSteps = 100;
	let isOptimizing = false;
	let results: Array<{smiles: string, score: number, step: number}> = [];
	let bestMolecule = '';
	let bestScore = 0;
	
	const properties = [
		{ value: 'QED', label: 'QED (药物相似性)', description: '评估分子的药物相似性' },
		{ value: 'LogP', label: 'LogP (脂水分配系数)', description: '评估分子的亲脂性' },
		{ value: 'SA', label: 'SA (合成可达性)', description: '评估分子的合成难易程度' },
		{ value: 'TPSA', label: 'TPSA (极性表面积)', description: '评估分子的极性表面积' }
	];
	
	async function optimizeMolecule() {
		isOptimizing = true;
		results = [];
		bestMolecule = '';
		bestScore = 0;
		
		// 模拟优化过程
		for (let step = 1; step <= optimizationSteps; step++) {
			await new Promise(resolve => setTimeout(resolve, 50));
			
			// 模拟生成优化后的分子
			const optimizedSmiles = generateOptimizedSmiles(inputSmiles, step);
			const score = Math.random() * 0.8 + 0.2; // 模拟评分
			
			const result = { smiles: optimizedSmiles, score, step };
			results = [...results, result];
			
			if (score > bestScore) {
				bestScore = score;
				bestMolecule = optimizedSmiles;
			}
			
			// 每10步更新一次界面
			if (step % 10 === 0) {
				results = results; // 触发响应式更新
			}
		}
		
		isOptimizing = false;
	}
	
	function generateOptimizedSmiles(baseSmiles: string, step: number): string {
		// 简单的SMILES变化模拟
		const variations = [
			'CC(C)CC(C(=O)O)N',
			'CC(C)C(C(=O)O)N',
			'CCC(C(=O)O)N',
			'CC(C(=O)O)N',
			'CCCC(C(=O)O)N',
			'CC(C)CCC(C(=O)O)N',
			'CC(C)CC(C(=O)O)NC',
			'CC(C)CC(C(=O)O)NCC',
			'CC(C)CC(C(=O)O)NCCC',
			'CC(C)CC(C(=O)O)NCCCC'
		];
		return variations[step % variations.length];
	}
	
	function downloadResults() {
		const csvContent = 'Step,SMILES,Score\n' + 
			results.map(r => `${r.step},${r.smiles},${r.score.toFixed(4)}`).join('\n');
		const blob = new Blob([csvContent], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'molmim_optimization_results.csv';
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>MolMIM - 分子优化模型</title>
</svelte:head>

<div class="max-w-6xl mx-auto space-y-8">
	<!-- 页面标题 -->
	<div class="text-center">
		<div class="flex items-center justify-center mb-4">
			<Microscope class="w-12 h-12 text-purple-600 mr-4" />
			<h1 class="text-4xl font-bold text-gray-900 dark:text-white">MolMIM</h1>
		</div>
		<p class="text-xl text-gray-600 dark:text-gray-300">
			基于生成式AI的分子优化与设计平台
		</p>
	</div>

	<!-- 功能介绍 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">模型介绍</h2>
		<div class="prose dark:prose-invert max-w-none">
			<p class="text-gray-700 dark:text-gray-300 mb-4">
				MolMIM是NVIDIA BioNeMo平台中的分子优化模型，专门用于生成具有特定性质的分子。该模型使用受控生成技术，在用户指定的Oracle函数指导下，浏览化学空间的学习内部表示，生成优化的分子结构。
			</p>
			
			<div class="grid md:grid-cols-3 gap-6 mt-6">
				<div class="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
					<h3 class="font-semibold text-purple-900 dark:text-purple-300 mb-2">核心功能</h3>
					<ul class="text-sm text-purple-800 dark:text-purple-200 space-y-1">
						<li>• 分子性质优化</li>
						<li>• 多目标优化</li>
						<li>• 受控分子生成</li>
						<li>• 化学空间探索</li>
					</ul>
				</div>
				
				<div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
					<h3 class="font-semibold text-blue-900 dark:text-blue-300 mb-2">技术特点</h3>
					<ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
						<li>• CMA-ES优化算法</li>
						<li>• 潜在空间搜索</li>
						<li>• 迭代优化过程</li>
						<li>• Oracle函数引导</li>
					</ul>
				</div>
				
				<div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
					<h3 class="font-semibold text-green-900 dark:text-green-300 mb-2">应用领域</h3>
					<ul class="text-sm text-green-800 dark:text-green-200 space-y-1">
						<li>• 药物发现</li>
						<li>• 先导化合物优化</li>
						<li>• 分子设计</li>
						<li>• 性质预测</li>
					</ul>
				</div>
			</div>
		</div>
	</div>

	<!-- 分子优化界面 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">分子优化</h2>
		
		<div class="grid lg:grid-cols-2 gap-8">
			<!-- 输入参数 -->
			<div class="space-y-6">
				<div>
					<label for="inputSmiles" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						起始分子 (SMILES)
					</label>
					<input
						id="inputSmiles"
						type="text"
						bind:value={inputSmiles}
						placeholder="例如：CCO"
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 dark:bg-gray-700 dark:text-white"
					/>
				</div>
				
				<div>
					<label for="targetProperty" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						目标性质
					</label>
					<select
						id="targetProperty"
						bind:value={targetProperty}
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 dark:bg-gray-700 dark:text-white"
					>
						{#each properties as prop}
							<option value={prop.value}>{prop.label}</option>
						{/each}
					</select>
					<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
						{properties.find(p => p.value === targetProperty)?.description}
					</p>
				</div>
				
				<div>
					<label for="optimizationSteps" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						优化步数 ({optimizationSteps})
					</label>
					<input
						id="optimizationSteps"
						type="range"
						bind:value={optimizationSteps}
						min="50"
						max="500"
						step="50"
						class="w-full"
					/>
					<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
						<span>快速 (50)</span>
						<span>深度 (500)</span>
					</div>
				</div>
				
				<button
					on:click={optimizeMolecule}
					disabled={isOptimizing}
					class="w-full flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					{#if isOptimizing}
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
						优化中... ({results.length}/{optimizationSteps})
					{:else}
						<Target class="w-4 h-4 mr-2" />
						开始优化
					{/if}
				</button>
			</div>
			
			<!-- 结果显示 -->
			<div class="space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white">优化结果</h3>
					{#if results.length > 0}
						<button
							on:click={downloadResults}
							class="flex items-center px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
						>
							<Download class="w-4 h-4 mr-1" />
							下载
						</button>
					{/if}
				</div>
				
				<!-- 最佳结果 -->
				{#if bestMolecule}
					<div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
						<div class="flex items-center mb-2">
							<TrendingUp class="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
							<span class="font-semibold text-green-900 dark:text-green-300">最佳分子</span>
						</div>
						<div class="text-sm font-mono text-green-800 dark:text-green-200 mb-1">{bestMolecule}</div>
						<div class="text-sm text-green-700 dark:text-green-300">评分: {bestScore.toFixed(4)}</div>
					</div>
				{/if}
				
				<!-- 优化历史 -->
				<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 h-64 overflow-y-auto">
					{#if results.length > 0}
						<div class="space-y-2">
							{#each results.slice(-10) as result}
								<div class="flex items-center justify-between bg-white dark:bg-gray-600 p-2 rounded border">
									<div class="flex-1">
										<div class="text-sm font-mono text-gray-800 dark:text-gray-200 truncate">{result.smiles}</div>
										<div class="text-xs text-gray-500 dark:text-gray-400">步骤 {result.step}</div>
									</div>
									<div class="text-sm font-semibold text-purple-600 dark:text-purple-400">
										{result.score.toFixed(3)}
									</div>
								</div>
							{/each}
						</div>
					{:else}
						<div class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
							<div class="text-center">
								<Microscope class="w-12 h-12 mx-auto mb-2 opacity-50" />
								<p>点击"开始优化"来优化分子</p>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>

	<!-- 工作流程 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">优化流程</h2>
		<div class="grid md:grid-cols-4 gap-4">
			<div class="text-center">
				<div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-purple-600 dark:text-purple-400 font-bold">1</span>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white mb-2">输入分子</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">提供起始分子的SMILES表示</p>
			</div>
			
			<div class="text-center">
				<div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-purple-600 dark:text-purple-400 font-bold">2</span>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white mb-2">设定目标</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">选择要优化的分子性质</p>
			</div>
			
			<div class="text-center">
				<div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-purple-600 dark:text-purple-400 font-bold">3</span>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white mb-2">迭代优化</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">使用CMA-ES算法搜索最优解</p>
			</div>
			
			<div class="text-center">
				<div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-purple-600 dark:text-purple-400 font-bold">4</span>
				</div>
				<h3 class="font-semibold text-gray-900 dark:text-white mb-2">获得结果</h3>
				<p class="text-sm text-gray-600 dark:text-gray-400">得到优化后的分子结构</p>
			</div>
		</div>
	</div>

	<!-- 相关资源 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">相关资源</h2>
		<div class="grid md:grid-cols-3 gap-4">
			<a
				href="https://developer.nvidia.com/zh-cn/blog/new-models-molmim-and-diffdock-power-molecule-generation-and-molecular-docking-in-bionemo/"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
			>
				<FileText class="w-6 h-6 text-purple-600 dark:text-purple-400 mr-3" />
				<div>
					<div class="font-semibold text-purple-900 dark:text-purple-300">官方博客</div>
					<div class="text-sm text-purple-700 dark:text-purple-400">NVIDIA开发者</div>
				</div>
				<ExternalLink class="w-4 h-4 text-purple-600 dark:text-purple-400 ml-auto" />
			</a>
			
			<a
				href="https://www.nvidia.com/en-us/clara/bionemo/"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
			>
				<ExternalLink class="w-6 h-6 text-green-600 dark:text-green-400 mr-3" />
				<div>
					<div class="font-semibold text-green-900 dark:text-green-300">BioNeMo平台</div>
					<div class="text-sm text-green-700 dark:text-green-400">NVIDIA Clara</div>
				</div>
				<ExternalLink class="w-4 h-4 text-green-600 dark:text-green-400 ml-auto" />
			</a>
			
			<a
				href="https://blogs.nvidia.cn/blog/drug-discovery-bionemo-generative-ai/"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
			>
				<ExternalLink class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" />
				<div>
					<div class="font-semibold text-blue-900 dark:text-blue-300">应用案例</div>
					<div class="text-sm text-blue-700 dark:text-blue-400">药物研发</div>
				</div>
				<ExternalLink class="w-4 h-4 text-blue-600 dark:text-blue-400 ml-auto" />
			</a>
		</div>
	</div>
</div> 