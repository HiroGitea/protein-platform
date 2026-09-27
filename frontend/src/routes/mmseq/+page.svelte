<script lang="ts">
	import { Search, Upload, Play, Download, Info, Database } from 'lucide-svelte';
	
	let querySequence = '';
	let selectedDatabase = 'uniref50';
	let selectedFile: File | null = null;
	let isSearching = false;
	let searchResults: any[] = [];
	
	const databases = [
		{ value: 'uniref50', label: 'UniRef50 - 蛋白质序列聚类数据库' },
		{ value: 'uniref90', label: 'UniRef90 - 高相似性蛋白质序列' },
		{ value: 'swissprot', label: 'SwissProt - 手工注释蛋白质数据库' },
		{ value: 'pfam', label: 'Pfam - 蛋白质家族数据库' }
	];
	
	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			selectedFile = target.files[0];
		}
	}
	
	async function startSearch() {
		if (!querySequence.trim() && !selectedFile) {
			alert('请输入查询序列或上传FASTA文件');
			return;
		}
		
		isSearching = true;
		searchResults = [];
		
		// 模拟搜索过程
		await new Promise(resolve => setTimeout(resolve, 2500));
		
		// 模拟搜索结果
		searchResults = [
			{
				id: 'P12345',
				description: 'Hypothetical protein ABC123',
				organism: 'Homo sapiens',
				identity: 95.2,
				coverage: 98.5,
				evalue: '1e-150',
				score: 542
			},
			{
				id: 'Q67890',
				description: 'Similar protein XYZ789',
				organism: 'Mus musculus',
				identity: 87.3,
				coverage: 92.1,
				evalue: '2e-120',
				score: 456
			},
			{
				id: 'R11111',
				description: 'Related enzyme DEF456',
				organism: 'Rattus norvegicus',
				identity: 76.8,
				coverage: 85.3,
				evalue: '5e-95',
				score: 321
			}
		];
		
		isSearching = false;
	}
	
	function downloadResults() {
		const csvContent = [
			'ID,Description,Organism,Identity(%),Coverage(%),E-value,Score',
			...searchResults.map(r => 
				`${r.id},"${r.description}","${r.organism}",${r.identity},${r.coverage},${r.evalue},${r.score}`
			)
		].join('\n');
		
		const blob = new Blob([csvContent], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'mmseqs_results.csv';
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>MMseqs2 - 序列搜索与聚类</title>
</svelte:head>

<div class="max-w-6xl mx-auto">
	<!-- 页面头部 -->
	<div class="mb-8">
		<div class="flex items-center mb-4">
			<div class="p-3 bg-green-500 rounded-lg mr-4">
				<Search class="w-8 h-8 text-white" />
			</div>
			<div>
				<h1 class="text-3xl font-bold text-gray-900 dark:text-white">MMseqs2</h1>
				<p class="text-gray-600 dark:text-gray-400">快速序列搜索和聚类工具</p>
			</div>
		</div>
		
		<div class="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg p-4">
			<div class="flex items-start">
				<Info class="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5 mr-3 flex-shrink-0" />
				<div class="text-sm text-green-800 dark:text-green-200">
					<p class="font-medium mb-1">关于MMseqs2</p>
					<p>MMseqs2是一个超快速的序列搜索和聚类工具，比BLAST快数百倍，支持大规模蛋白质序列分析和同源性搜索。</p>
				</div>
			</div>
		</div>
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
		<!-- 搜索输入区域 -->
		<div class="space-y-6">
			<div class="card">
				<h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
					序列搜索
				</h2>
				
				<!-- 查询序列输入 -->
				<div class="mb-4">
					<label for="query" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						查询序列 (FASTA格式)
					</label>
					<textarea
						id="query"
						bind:value={querySequence}
						rows="6"
						class="input resize-none"
						placeholder="请输入查询序列，例如：
>Query_sequence
MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
					></textarea>
				</div>
				
				<!-- 数据库选择 -->
				<div class="mb-4">
					<label for="database" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						目标数据库
					</label>
					<select id="database" bind:value={selectedDatabase} class="input">
						{#each databases as db}
							<option value={db.value}>{db.label}</option>
						{/each}
					</select>
				</div>
				
				<!-- 文件上传 -->
				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						或上传FASTA文件
					</label>
					<div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
						<Upload class="w-8 h-8 text-gray-400 mx-auto mb-2" />
						<p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
							支持多序列FASTA文件
						</p>
						<input
							type="file"
							accept=".fasta,.fa,.txt"
							on:change={handleFileSelect}
							class="hidden"
							id="file-upload"
						/>
						<label for="file-upload" class="btn btn-secondary cursor-pointer">
							选择文件
						</label>
						{#if selectedFile}
							<p class="text-sm text-green-600 dark:text-green-400 mt-2">
								已选择: {selectedFile.name}
							</p>
						{/if}
					</div>
				</div>
				
				<!-- 搜索按钮 -->
				<button
					on:click={startSearch}
					disabled={isSearching || (!querySequence.trim() && !selectedFile)}
					class="btn btn-primary w-full flex items-center justify-center"
				>
					{#if isSearching}
						<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
						搜索中...
					{:else}
						<Search class="w-5 h-5 mr-2" />
						开始搜索
					{/if}
				</button>
			</div>
			
			<!-- 搜索参数 -->
			<div class="card">
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
					搜索参数
				</h3>
				<div class="space-y-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							E-value阈值
						</label>
						<select class="input">
							<option>1e-3</option>
							<option selected>1e-5</option>
							<option>1e-10</option>
							<option>1e-20</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							最大目标序列数
						</label>
						<select class="input">
							<option>100</option>
							<option selected>500</option>
							<option>1000</option>
							<option>5000</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							敏感度
						</label>
						<select class="input">
							<option>快速</option>
							<option selected>标准</option>
							<option>敏感</option>
							<option>超敏感</option>
						</select>
					</div>
				</div>
			</div>
		</div>

		<!-- 搜索结果区域 -->
		<div class="space-y-6">
			{#if searchResults.length > 0}
				<div class="card">
					<div class="flex items-center justify-between mb-4">
						<h2 class="text-xl font-semibold text-gray-900 dark:text-white">
							搜索结果 ({searchResults.length} 条)
						</h2>
						<button
							on:click={downloadResults}
							class="btn btn-secondary flex items-center"
						>
							<Download class="w-4 h-4 mr-2" />
							下载结果
						</button>
					</div>
					
					<!-- 结果列表 -->
					<div class="space-y-3 max-h-96 overflow-y-auto">
						{#each searchResults as result, index}
							<div class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
								<div class="flex items-start justify-between mb-2">
									<div>
										<h3 class="font-medium text-gray-900 dark:text-white">
											{result.id}
										</h3>
										<p class="text-sm text-gray-600 dark:text-gray-400">
											{result.description}
										</p>
										<p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
											{result.organism}
										</p>
									</div>
									<span class="text-xs bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 px-2 py-1 rounded">
										#{index + 1}
									</span>
								</div>
								
								<div class="grid grid-cols-2 gap-4 text-sm">
									<div>
										<span class="text-gray-500 dark:text-gray-400">相似度:</span>
										<span class="font-medium text-gray-900 dark:text-white ml-1">
											{result.identity}%
										</span>
									</div>
									<div>
										<span class="text-gray-500 dark:text-gray-400">覆盖度:</span>
										<span class="font-medium text-gray-900 dark:text-white ml-1">
											{result.coverage}%
										</span>
									</div>
									<div>
										<span class="text-gray-500 dark:text-gray-400">E-value:</span>
										<span class="font-medium text-gray-900 dark:text-white ml-1">
											{result.evalue}
										</span>
									</div>
									<div>
										<span class="text-gray-500 dark:text-gray-400">得分:</span>
										<span class="font-medium text-gray-900 dark:text-white ml-1">
											{result.score}
										</span>
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{:else}
				<div class="card">
					<div class="text-center py-12">
						<Database class="w-16 h-16 text-gray-400 mx-auto mb-4" />
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
							等待搜索
						</h3>
						<p class="text-gray-600 dark:text-gray-400">
							请输入查询序列并开始搜索
						</p>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div> 