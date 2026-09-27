<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import MoleculeViewer from '$lib/components/MoleculeViewer.svelte';
  import type { PluginUIContext } from 'molstar/lib/mol-plugin-ui/context';
  
  let proteinFile: File | null = null;
  let ligandFile: File | null = null;
  let moleculeViewer: MoleculeViewer;
  let plugin: PluginUIContext | undefined;
  let isLoading = false;
  let error: string | null = null;
  
  // 处理蛋白质文件上传
  function handleProteinFileChange(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      proteinFile = target.files[0];
      console.log('选择了蛋白质文件:', proteinFile.name);
    }
  }
  
  // 处理配体文件上传
  function handleLigandFileChange(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      ligandFile = target.files[0];
      console.log('选择了配体文件:', ligandFile.name);
    }
  }
  
  // 从URL加载文件
  async function loadFromUrl(url: string, filename: string, type: 'protein' | 'ligand') {
    try {
      isLoading = true;
      error = null;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`无法获取文件: ${response.status} ${response.statusText}`);
      }
      
      const blob = await response.blob();
      const file = new File([blob], filename, { type: 'text/plain' });
      
      if (type === 'protein') {
        proteinFile = file;
      } else {
        ligandFile = file;
      }
      
      console.log(`从URL加载${type}文件成功:`, filename);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      error = `加载${type}文件失败: ${errorMsg}`;
      console.error('从URL加载文件失败:', err);
    } finally {
      isLoading = false;
    }
  }
  
  // 加载示例蛋白质
  async function loadExampleProtein() {
    await loadFromUrl('/examples/target_protein.pdb', 'target_protein.pdb', 'protein');
  }
  
  // 加载示例配体
  async function loadExampleLigand() {
    await loadFromUrl('/examples/rank1_confidence-0.6142062544822693.sdf', 'rank1_ligand.sdf', 'ligand');
  }
  
  // 加载示例蛋白质-配体复合物
  async function loadExampleComplex() {
    try {
      isLoading = true;
      error = null;
      
      // 同时加载蛋白质和配体
      await Promise.all([
        loadFromUrl('/examples/target_protein.pdb', 'target_protein.pdb', 'protein'),
        loadFromUrl('/examples/rank1_confidence-0.6142062544822693.sdf', 'rank1_ligand.sdf', 'ligand')
      ]);
      
      console.log('示例复合物加载成功');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      error = `加载示例复合物失败: ${errorMsg}`;
      console.error('加载示例复合物失败:', err);
    } finally {
      isLoading = false;
    }
  }
  
  // 清除所有文件
  function clearFiles() {
    proteinFile = null;
    ligandFile = null;
    if (moleculeViewer) {
      moleculeViewer.clear();
    }
  }
  
  // 重新加载
  function reload() {
    if (moleculeViewer) {
      moleculeViewer.reload();
    }
  }
  
  // 处理插件就绪事件
  function handlePluginReady(event: CustomEvent<PluginUIContext>) {
    plugin = event.detail;
    console.log('Mol*插件已就绪');
  }
  
  // 加载所有配体姿态
  async function loadAllLigands() {
    if (moleculeViewer) {
      await moleculeViewer.loadAllLigands();
    } else {
      error = '分子查看器未初始化';
    }
  }
</script>

<svelte:head>
  <title>分子可视化 - 生物信息学平台</title>
  <meta name="description" content="使用Mol*进行分子结构可视化" />
  <!-- 预加载Molstar资源 -->
  <link rel="preload" href="/vendor/molstar/molstar.js" as="script" crossorigin="anonymous">
  <link rel="preload" href="/vendor/molstar/molstar.css" as="style">
  <link rel="stylesheet" href="/vendor/molstar/molstar.css">
</svelte:head>

<div class="container mx-auto px-4 py-8">
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
      分子可视化
    </h1>
    <p class="text-gray-600 dark:text-gray-300">
      使用Mol*进行蛋白质和配体的3D结构可视化。支持PDB、SDF、MOL等多种格式。
    </p>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
    <!-- 控制面板 -->
    <div class="lg:col-span-1">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          文件控制
        </h2>
        
        <!-- 蛋白质文件上传 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            蛋白质文件 (PDB)
          </label>
          <input
            type="file"
            accept=".pdb,.cif"
            on:change={handleProteinFileChange}
            class="block w-full text-sm text-gray-500 dark:text-gray-400
                   file:mr-4 file:py-2 file:px-4
                   file:rounded-full file:border-0
                   file:text-sm file:font-semibold
                   file:bg-blue-50 file:text-blue-700
                   hover:file:bg-blue-100
                   dark:file:bg-blue-900 dark:file:text-blue-300"
          />
          {#if proteinFile}
            <p class="mt-1 text-xs text-green-600 dark:text-green-400">
              已选择: {proteinFile.name}
            </p>
          {/if}
        </div>
        
        <!-- 配体文件上传 -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            配体文件 (SDF/MOL)
          </label>
          <input
            type="file"
            accept=".sdf,.mol,.mol2"
            on:change={handleLigandFileChange}
            class="block w-full text-sm text-gray-500 dark:text-gray-400
                   file:mr-4 file:py-2 file:px-4
                   file:rounded-full file:border-0
                   file:text-sm file:font-semibold
                   file:bg-green-50 file:text-green-700
                   hover:file:bg-green-100
                   dark:file:bg-green-900 dark:file:text-green-300"
          />
          {#if ligandFile}
            <p class="mt-1 text-xs text-green-600 dark:text-green-400">
              已选择: {ligandFile.name}
            </p>
          {/if}
        </div>
        
        <!-- 示例文件 -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            示例文件
          </h3>
          <div class="space-y-2">
            <button
              on:click={loadExampleProtein}
              class="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              disabled={isLoading}
            >
              加载示例蛋白质
            </button>
            <button
              on:click={loadExampleLigand}
              class="w-full px-3 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              disabled={isLoading}
            >
              加载示例配体
            </button>
            <button
              on:click={loadExampleComplex}
              class="w-full px-3 py-2 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
              disabled={isLoading}
            >
              加载示例复合物
            </button>
            <button
              on:click={loadAllLigands}
              class="w-full px-3 py-2 text-sm bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
              disabled={isLoading}
            >
              添加所有配体 (20个姿态)
            </button>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="space-y-2">
          <button
            on:click={reload}
            class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            disabled={isLoading || (!proteinFile && !ligandFile)}
          >
            重新加载
          </button>
          
          <button
            on:click={clearFiles}
            class="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            disabled={isLoading}
          >
            清除所有
          </button>
        </div>
        
        <!-- 状态信息 -->
        {#if isLoading}
          <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900 rounded-md">
            <div class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span class="text-sm text-blue-700 dark:text-blue-300">加载中...</span>
            </div>
          </div>
        {/if}
        
        {#if error}
          <div class="mt-4 p-3 bg-red-50 dark:bg-red-900 rounded-md">
            <p class="text-sm text-red-700 dark:text-red-300">{error}</p>
            <button
              on:click={() => error = null}
              class="mt-2 text-xs text-red-600 dark:text-red-400 hover:underline"
            >
              关闭
            </button>
          </div>
        {/if}
        
        <!-- 使用说明 -->
        <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            使用说明
          </h3>
          <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <li>• 支持PDB、CIF格式的蛋白质文件</li>
            <li>• 支持SDF、MOL格式的配体文件</li>
            <li>• 可以单独加载蛋白质或配体</li>
            <li>• 鼠标拖拽旋转，滚轮缩放</li>
            <li>• 右键菜单提供更多选项</li>
            <li>• 示例文件来自DiffDock对接结果</li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- 分子可视化区域 -->
    <div class="lg:col-span-3">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
          3D结构视图
        </h2>
        
        <div class="h-[600px] w-full relative">
          <MoleculeViewer
            bind:this={moleculeViewer}
            {proteinFile}
            {ligandFile}
            on:pluginReady={handlePluginReady}
          />
          
          {#if !proteinFile && !ligandFile}
            <div class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-lg">
              <div class="text-center text-gray-500 dark:text-gray-400">
                <svg class="mx-auto h-12 w-12 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a4 4 0 004-4V5z" />
                </svg>
                <p class="text-lg font-medium">请上传分子结构文件</p>
                <p class="text-sm">支持PDB、SDF、MOL等格式</p>
                <p class="text-sm mt-2">或点击左侧按钮加载示例文件</p>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div> 