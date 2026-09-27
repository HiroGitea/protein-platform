<script lang="ts">
	import { Atom, Upload, Play, Download, Info, Zap } from 'lucide-svelte';
	
	let proteinFile: File | null = null;
	let ligandFile: File | null = null;
	let isDocking = false;
	let dockingResult: any = null;
	
	function handleProteinFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			proteinFile = target.files[0];
		}
	}
	
	function handleLigandFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			ligandFile = target.files[0];
		}
	}
	
	async function startDocking() {
		if (!proteinFile || !ligandFile) {
			alert('请上传蛋白质和配体文件');
			return;
		}
		
		isDocking = true;
		dockingResult = null;
		
		// 模拟对接过程
		await new Promise(resolve => setTimeout(resolve, 4000));
		
		// 模拟对接结果
		dockingResult = {
			poses: [
				{ id: 1, score: -8.5, rmsd: 1.2, confidence: 0.92 },
				{ id: 2, score: -7.8, rmsd: 1.8, confidence: 0.87 },
				{ id: 3, score: -7.3, rmsd: 2.1, confidence: 0.81 },
				{ id: 4, score: -6.9, rmsd: 2.5, confidence: 0.76 },
				{ id: 5, score: -6.4, rmsd: 3.0, confidence: 0.71 }
			],
			bestPose: {
				score: -8.5,
				rmsd: 1.2,
				confidence: 0.92,
				interactions: [
					'Hydrogen bond: LIG-O1 ... ARG123-NH',
					'Hydrophobic: LIG-C5 ... PHE456',
					'π-π stacking: LIG-Ring ... TYR789'
				]
			}
		};
		
		isDocking = false;
	}
	
	function downloadResults() {
		const resultData = {
			protein: proteinFile?.name,
			ligand: ligandFile?.name,
			timestamp: new Date().toISOString(),
			results: dockingResult
		};
		
		const blob = new Blob([JSON.stringify(resultData, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'diffdock_results.json';
		a.click();
		URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>DiffDock - 分子对接预测</title>
</svelte:head>

<div class="max-w-6xl mx-auto">
	<!-- 页面头部 -->
	<div class="mb-8">
		<div class="flex items-center mb-4">
			<div class="p-3 bg-purple-500 rounded-lg mr-4">
				<Atom class="w-8 h-8 text-white" />
			</div>
			<div>
				<h1 class="text-3xl font-bold text-gray-900 dark:text-white">DiffDock</h1>
				<p class="text-gray-600 dark:text-gray-400">基于扩散模型的分子对接预测</p>
			</div>
		</div>
		
		<div class="bg-purple-50 dark:bg-purple-900 border border-purple-200 dark:border-purple-700 rounded-lg p-4">
			<div class="flex items-start">
				<Info class="w-5 h-5 text-purple-600 dark:text-purple-400 mt-0.5 mr-3 flex-shrink-0" />
				<div class="text-sm text-purple-800 dark:text-purple-200">
					<p class="font-medium mb-1">关于DiffDock</p>
					<p>DiffDock是一个基于扩散模型的分子对接工具，能够预测小分子配体与蛋白质的结合模式，广泛应用于药物发现和分子设计。</p>
				</div>
			</div>
		</div>
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
		<!-- 输入区域 -->
		<div class="space-y-6">
			<div class="card">
				<h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
					分子对接输入
				</h2>
				
				<!-- 蛋白质文件上传 -->
				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						蛋白质结构文件 (PDB格式)
					</label>
					<div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
						<Upload class="w-8 h-8 text-gray-400 mx-auto mb-2" />
						<p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
							上传蛋白质PDB文件
						</p>
						<input
							type="file"
							accept=".pdb,.ent"
							on:change={handleProteinFileSelect}
							class="hidden"
							id="protein-upload"
						/>
						<label for="protein-upload" class="btn btn-secondary cursor-pointer">
							选择蛋白质文件
						</label>
						{#if proteinFile}
							<p class="text-sm text-green-600 dark:text-green-400 mt-2">
								已选择: {proteinFile.name}
							</p>
						{/if}
					</div>
				</div>
				
				<!-- 配体文件上传 -->
				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						配体分子文件 (SDF/MOL格式)
					</label>
					<div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
						<Upload class="w-8 h-8 text-gray-400 mx-auto mb-2" />
						<p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
							上传配体分子文件
						</p>
						<input
							type="file"
							accept=".sdf,.mol,.mol2"
							on:change={handleLigandFileSelect}
							class="hidden"
							id="ligand-upload"
						/>
						<label for="ligand-upload" class="btn btn-secondary cursor-pointer">
							选择配体文件
						</label>
						{#if ligandFile}
							<p class="text-sm text-green-600 dark:text-green-400 mt-2">
								已选择: {ligandFile.name}
							</p>
						{/if}
					</div>
				</div>
				
				<!-- 对接按钮 -->
				<button
					on:click={startDocking}
					disabled={isDocking || !proteinFile || !ligandFile}
					class="btn btn-primary w-full flex items-center justify-center"
				>
					{#if isDocking}
						<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
						对接中...
					{:else}
						<Zap class="w-5 h-5 mr-2" />
						开始分子对接
					{/if}
				</button>
			</div>
			
			<!-- 对接参数 -->
			<div class="card">
				<h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
					对接参数
				</h3>
				<div class="space-y-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							生成构象数量
						</label>
						<select class="input">
							<option>5</option>
							<option selected>10</option>
							<option>20</option>
							<option>50</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							采样步数
						</label>
						<select class="input">
							<option>100</option>
							<option selected>200</option>
							<option>500</option>
							<option>1000</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
							结合位点预测
						</label>
						<select class="input">
							<option selected>自动检测</option>
							<option>指定残基</option>
							<option>全蛋白扫描</option>
						</select>
					</div>
				</div>
			</div>
		</div>

		<!-- 结果区域 -->
		<div class="space-y-6">
			{#if dockingResult}
				<div class="card">
					<div class="flex items-center justify-between mb-4">
						<h2 class="text-xl font-semibold text-gray-900 dark:text-white">
							对接结果
						</h2>
						<button
							on:click={downloadResults}
							class="btn btn-secondary flex items-center"
						>
							<Download class="w-4 h-4 mr-2" />
							下载结果
						</button>
					</div>
					
					<!-- 最佳构象 -->
					<div class="mb-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900 dark:to-blue-900 rounded-lg">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
							最佳对接构象
						</h3>
						<div class="grid grid-cols-3 gap-4 mb-4">
							<div class="text-center">
								<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
									{dockingResult.bestPose.score}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">对接得分</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
									{dockingResult.bestPose.rmsd}Å
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">RMSD</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
									{(dockingResult.bestPose.confidence * 100).toFixed(0)}%
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">置信度</div>
							</div>
						</div>
						
						<!-- 相互作用 -->
						<div>
							<h4 class="font-medium text-gray-900 dark:text-white mb-2">关键相互作用</h4>
							<div class="space-y-1">
								{#each dockingResult.bestPose.interactions as interaction}
									<div class="text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 px-3 py-1 rounded">
										{interaction}
									</div>
								{/each}
							</div>
						</div>
					</div>
					
					<!-- 3D结构预览 -->
					<div class="mb-6">
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
							3D结构预览
						</h3>
						<div class="bg-gray-100 dark:bg-gray-700 rounded-lg h-64 flex items-center justify-center">
							<div class="text-center text-gray-500 dark:text-gray-400">
								<Atom class="w-12 h-12 mx-auto mb-2" />
								<p>分子对接结构查看器</p>
								<p class="text-sm">(需要集成3D分子查看器)</p>
							</div>
						</div>
					</div>
					
					<!-- 所有构象列表 -->
					<div>
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">
							所有对接构象
						</h3>
						<div class="space-y-2 max-h-64 overflow-y-auto">
							{#each dockingResult.poses as pose, index}
								<div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
									<div class="flex items-center">
										<span class="w-8 h-8 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full flex items-center justify-center text-sm font-medium mr-3">
											{pose.id}
										</span>
										<div>
											<div class="text-sm font-medium text-gray-900 dark:text-white">
												构象 {pose.id}
											</div>
											<div class="text-xs text-gray-500 dark:text-gray-400">
												置信度: {(pose.confidence * 100).toFixed(0)}%
											</div>
										</div>
									</div>
									<div class="text-right">
										<div class="text-sm font-medium text-gray-900 dark:text-white">
											{pose.score}
										</div>
										<div class="text-xs text-gray-500 dark:text-gray-400">
											RMSD: {pose.rmsd}Å
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{:else}
				<div class="card">
					<div class="text-center py-12">
						<Atom class="w-16 h-16 text-gray-400 mx-auto mb-4" />
						<h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
							等待对接
						</h3>
						<p class="text-gray-600 dark:text-gray-400">
							请上传蛋白质和配体文件并开始对接
						</p>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div> 