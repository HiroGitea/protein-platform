<script lang="ts">
	import { Beaker, Download, Play, FileText, Github, ExternalLink } from 'lucide-svelte';
	
	let smiles = 'CCO';
	let numMolecules = 10;
	let temperature = 1.0;
	let isGenerating = false;
	let results: string[] = [];
	
	async function generateMolecules() {
		isGenerating = true;
		// 模拟API调用
		await new Promise(resolve => setTimeout(resolve, 2000));
		
		// 模拟生成的分子
		results = [
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
		].slice(0, numMolecules);
		
		isGenerating = false;
	}
	
	function downloadResults() {
		const blob = new Blob([results.join('\n')], { type: 'text/plain' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'genmol_results.txt';
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>GenMol - 分子生成模型</title>
</svelte:head>

<div class="max-w-6xl mx-auto space-y-8">
	<!-- 页面标题 -->
	<div class="text-center">
		<div class="flex items-center justify-center mb-4">
			<Beaker class="w-12 h-12 text-blue-600 mr-4" />
			<h1 class="text-4xl font-bold text-gray-900 dark:text-white">GenMol</h1>
		</div>
		<p class="text-xl text-gray-600 dark:text-gray-300">
			基于离散扩散的通用分子生成模型
		</p>
	</div>

	<!-- 功能介绍 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">模型介绍</h2>
		<div class="prose dark:prose-invert max-w-none">
			<p class="text-gray-700 dark:text-gray-300 mb-4">
				GenMol是一个基于离散扩散的通用分子生成框架，能够处理多种药物发现场景。该模型使用SAFE（Sequential Attachment-based Fragment Embedding）序列表示，通过非自回归双向并行解码生成分子。
			</p>
			
			<div class="grid md:grid-cols-2 gap-6 mt-6">
				<div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
					<h3 class="font-semibold text-blue-900 dark:text-blue-300 mb-2">主要特性</h3>
					<ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
						<li>• 从头分子生成</li>
						<li>• 片段约束生成</li>
						<li>• 目标导向优化</li>
						<li>• 先导化合物优化</li>
					</ul>
				</div>
				
				<div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
					<h3 class="font-semibold text-green-900 dark:text-green-300 mb-2">技术优势</h3>
					<ul class="text-sm text-green-800 dark:text-green-200 space-y-1">
						<li>• 并行解码，效率更高</li>
						<li>• 片段重掩蔽策略</li>
						<li>• 分子上下文引导</li>
						<li>• SAFE序列表示</li>
					</ul>
				</div>
			</div>
		</div>
	</div>

	<!-- 使用界面 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">分子生成</h2>
		
		<div class="grid lg:grid-cols-2 gap-8">
			<!-- 输入参数 -->
			<div class="space-y-6">
				<div>
					<label for="smiles" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						输入SMILES（可选，用于引导生成）
					</label>
					<input
						id="smiles"
						type="text"
						bind:value={smiles}
						placeholder="例如：CCO 或留空进行从头生成"
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
					/>
				</div>
				
				<div>
					<label for="numMolecules" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						生成分子数量
					</label>
					<input
						id="numMolecules"
						type="number"
						bind:value={numMolecules}
						min="1"
						max="100"
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
					/>
				</div>
				
				<div>
					<label for="temperature" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						温度参数 ({temperature})
					</label>
					<input
						id="temperature"
						type="range"
						bind:value={temperature}
						min="0.1"
						max="2.0"
						step="0.1"
						class="w-full"
					/>
					<div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
						<span>保守 (0.1)</span>
						<span>多样 (2.0)</span>
					</div>
				</div>
				
				<button
					on:click={generateMolecules}
					disabled={isGenerating}
					class="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					{#if isGenerating}
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
						生成中...
					{:else}
						<Play class="w-4 h-4 mr-2" />
						开始生成
					{/if}
				</button>
			</div>
			
			<!-- 结果显示 -->
			<div class="space-y-4">
				<div class="flex items-center justify-between">
					<h3 class="text-lg font-semibold text-gray-900 dark:text-white">生成结果</h3>
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
				
				<div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 h-80 overflow-y-auto">
					{#if results.length > 0}
						<div class="space-y-2">
							{#each results as smiles, index}
								<div class="flex items-center justify-between bg-white dark:bg-gray-600 p-2 rounded border">
									<span class="text-sm font-mono text-gray-800 dark:text-gray-200">{smiles}</span>
									<span class="text-xs text-gray-500 dark:text-gray-400">#{index + 1}</span>
								</div>
							{/each}
						</div>
					{:else}
						<div class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
							<div class="text-center">
								<Beaker class="w-12 h-12 mx-auto mb-2 opacity-50" />
								<p>点击"开始生成"来生成分子</p>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>

	<!-- 使用说明 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">使用说明</h2>
		<div class="grid md:grid-cols-2 gap-6">
			<div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">输入参数</h3>
				<ul class="space-y-2 text-gray-700 dark:text-gray-300">
					<li><strong>SMILES：</strong>可选的引导分子，留空则进行从头生成</li>
					<li><strong>生成数量：</strong>要生成的分子数量（1-100）</li>
					<li><strong>温度：</strong>控制生成多样性，值越高越多样</li>
				</ul>
			</div>
			
			<div>
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">应用场景</h3>
				<ul class="space-y-2 text-gray-700 dark:text-gray-300">
					<li><strong>药物发现：</strong>生成具有特定性质的候选分子</li>
					<li><strong>先导优化：</strong>基于已知分子生成类似物</li>
					<li><strong>化学空间探索：</strong>发现新的化学结构</li>
				</ul>
			</div>
		</div>
	</div>

	<!-- 相关资源 -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
		<h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">相关资源</h2>
		<div class="grid md:grid-cols-3 gap-4">
			<a
				href="https://arxiv.org/abs/2501.06158"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
			>
				<FileText class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3" />
				<div>
					<div class="font-semibold text-blue-900 dark:text-blue-300">论文</div>
					<div class="text-sm text-blue-700 dark:text-blue-400">arXiv预印本</div>
				</div>
				<ExternalLink class="w-4 h-4 text-blue-600 dark:text-blue-400 ml-auto" />
			</a>
			
			<a
				href="https://github.com/NVIDIA/GenMol"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
			>
				<Github class="w-6 h-6 text-gray-600 dark:text-gray-400 mr-3" />
				<div>
					<div class="font-semibold text-gray-900 dark:text-gray-300">代码</div>
					<div class="text-sm text-gray-700 dark:text-gray-400">GitHub仓库</div>
				</div>
				<ExternalLink class="w-4 h-4 text-gray-600 dark:text-gray-400 ml-auto" />
			</a>
			
			<a
				href="https://developer.nvidia.com/zh-cn/blog/evaluating-genmol-as-a-generalist-foundation-model-for-molecular-generation/"
				target="_blank"
				rel="noopener noreferrer"
				class="flex items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
			>
				<ExternalLink class="w-6 h-6 text-green-600 dark:text-green-400 mr-3" />
				<div>
					<div class="font-semibold text-green-900 dark:text-green-300">博客</div>
					<div class="text-sm text-green-700 dark:text-green-400">NVIDIA开发者</div>
				</div>
				<ExternalLink class="w-4 h-4 text-green-600 dark:text-green-400 ml-auto" />
			</a>
		</div>
	</div>
</div> 