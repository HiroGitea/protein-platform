<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  import { browser } from '$app/environment';
  import { createMolstarPlugin, loadStructureFromFile, loadSdfFile, getFormatFromFile, loadAllPoses } from '$lib/utils/molstar-loader';
  import type { PluginUIContext } from 'molstar/lib/mol-plugin-ui/context';
  
  export let proteinFile: File | null = null;
  export let ligandFile: File | null = null;
  
  let container: HTMLElement;
  let _plugin: PluginUIContext | undefined;
  let loaded = false;
  let loading = false;
  let error: string | null = null;
  
  // 提供获取插件实例的方法
  export function getPlugin(): PluginUIContext | undefined {
    return _plugin;
  }
  
  const dispatch = createEventDispatcher();
  
  // 当插件实例可用时，通知父组件
  $: if (_plugin) {
    dispatch('pluginReady', _plugin);
  }
  
  // 监听文件变化
  $: if (browser && loaded && _plugin) {
    if (proteinFile || ligandFile) {
      loadMolecules();
    }
  }
  
  onMount(async () => {
    if (browser && container) {
      // 先添加样式，确保容器有正确的尺寸
      addCustomStyles();
      
      // 等待下一个tick确保DOM已更新
      await tick();
      
      // 确保容器可见
      container.style.visibility = 'visible';
      container.style.display = 'block';
      container.style.position = 'relative';
      container.style.minHeight = '400px';
      
      // 再次等待DOM更新
      await tick();
      
      // 初始化插件
      initMolstarPlugin();
    }
  });
  
  onDestroy(() => {
    if (browser && _plugin) {
      try {
        _plugin.dispose();
      } catch (error) {
        console.error('销毁 Molstar 插件时出错:', error);
      }
    }
  });
  
  // 添加自定义CSS以调整Molstar UI
  function addCustomStyles() {
    if (!browser) return;
    
    const style = document.createElement('style');
    style.textContent = `
      /* 设置深色背景和界面样式 */
      .msp-plugin {
        background-color: #000000;
      }
      
      /* 隐藏控制栏 */
      .msp-viewport-controls-buttons {
        display: none !important;
      }
      
      /* 隐藏导航按钮 */
      .msp-viewport-controls {
        display: none !important;
      }
      
      /* 隐藏其他控制元素 */
      .msp-layout-region-top-left, .msp-layout-region-top-right, 
      .msp-layout-region-left, .msp-layout-region-right {
        display: none !important;
      }
      
      /* 确保视图占据整个容器 */
      .msp-viewport {
        width: 100% !important;
        height: 100% !important;
      }
      
      /* 移除不必要的边框和间距 */
      .msp-layout-viewport {
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
      }
    `;
    
    document.head.appendChild(style);
  }
  
  // 初始化Mol*插件
  async function initMolstarPlugin() {
    if (!browser || !container) return;
    
    try {
      loading = true;
      error = null;
      
      // 添加检查容器尺寸的日志
      console.log('初始化Mol*插件，容器尺寸:', {
        clientWidth: container.clientWidth,
        clientHeight: container.clientHeight,
        offsetWidth: container.offsetWidth,
        offsetHeight: container.offsetHeight,
        boundingRect: container.getBoundingClientRect(),
        style: {
          width: container.style.width,
          height: container.style.height,
          display: container.style.display,
          visibility: container.style.visibility,
          position: container.style.position
        }
      });
      
      // 创建插件实例
      _plugin = await createMolstarPlugin(container);
      
      if (_plugin) {
        console.log('Mol*插件创建成功');
        loaded = true;
        
        // 如果已有文件，则加载
        if (proteinFile || ligandFile) {
          await loadMolecules();
        }
      } else {
        console.error('Mol*插件创建失败，返回了undefined');
        error = '无法创建Mol*可视化插件';
      }
    } catch (err) {
      console.error('初始化Mol*插件时出错:', err);
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loading = false;
    }
  }
  
  // 加载分子文件
  async function loadMolecules() {
    if (!_plugin || (!proteinFile && !ligandFile)) return;
    
    try {
      loading = true;
      error = null;
      console.log('开始加载分子文件');
      
      // 清除当前视图
      await _plugin.clear();
      
      // 特殊情况：仅有配体文件，没有蛋白质文件
      if (!proteinFile && ligandFile) {
        try {
          console.log(`尝试独立加载配体文件: ${ligandFile.name} (${ligandFile.size} 字节)`);
          // 使用专用方法加载SDF
          if (getFormatFromFile(ligandFile) === 'sdf') {
            await loadSdfFile(_plugin, ligandFile);
          } else {
            // 其他格式仍使用常规方法
            await loadStructureFromFile(_plugin, ligandFile, 'ball-and-stick');
          }
          console.log('配体文件加载成功');
          resetView();
          return;
        } catch (err) {
          const errMsg = err instanceof Error ? err.message : String(err);
          console.error('独立加载配体文件时出错:', errMsg);
          error = `配体加载失败: ${errMsg}`;
          loading = false;
          return;
        }
      }
      
      // 常规情况：有蛋白质文件，或两种文件都有
      
      // 先加载蛋白质文件
      if (proteinFile) {
        try {
          console.log(`尝试加载蛋白质文件: ${proteinFile.name} (${proteinFile.size} 字节)`);
          await loadStructureFromFile(_plugin, proteinFile, 'cartoon');
          console.log('蛋白质文件加载成功');
        } catch (err) {
          const errMsg = err instanceof Error ? err.message : String(err);
          console.error('加载蛋白质文件时出错:', errMsg);
          error = `蛋白质加载失败: ${errMsg}`;
          loading = false;
          return;
        }
      }
      
      // 再加载配体文件
      if (ligandFile) {
        try {
          console.log(`尝试加载配体文件: ${ligandFile.name} (${ligandFile.size} 字节)`);
          // 使用专用方法加载SDF
          if (getFormatFromFile(ligandFile) === 'sdf') {
            await loadSdfFile(_plugin, ligandFile);
          } else {
            // 其他格式仍使用常规方法
            await loadStructureFromFile(_plugin, ligandFile, 'ball-and-stick');
          }
          console.log('配体文件加载成功');
        } catch (err) {
          const errMsg = err instanceof Error ? err.message : String(err);
          console.error('加载配体文件时出错:', errMsg);
          if (error) {
            error = error + `\n配体加载失败: ${errMsg}`;
          } else {
            error = `配体加载失败: ${errMsg}`;
          }
        }
      }
      
      // 重置视图
      resetView();
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      console.error('加载分子文件时出错:', errMsg);
      error = `加载失败: ${errMsg}`;
    } finally {
      loading = false;
    }
  }
  
  // 重置视图
  function resetView() {
    if (_plugin?.canvas3d) {
      _plugin.canvas3d.requestCameraReset();
    }
  }
  
  // 重新加载
  export async function reload() {
    if (proteinFile || ligandFile) {
      await loadMolecules();
    }
  }
  
  // 清除视图
  export async function clear() {
    if (_plugin) {
      await _plugin.clear();
    }
  }
  
  // 加载所有配体姿态
  export async function loadAllLigands() {
    if (!_plugin) {
      console.error('Mol*插件未初始化');
      return;
    }
    
    try {
      loading = true;
      error = null;
      console.log('开始加载所有配体姿态');
      
      // 生成所有配体文件的URL列表
      const ligandUrls: string[] = [];
      for (let i = 1; i <= 20; i++) {
        // 根据examples目录中的文件命名规律生成URL
        // 这里我们需要读取实际的文件名
        const files = [
          `/examples/rank${i}_confidence-0.6142062544822693.sdf`,
          `/examples/rank${i}_confidence-1.0697367191314697.sdf`,
          `/examples/rank${i}_confidence-1.079310417175293.sdf`,
          `/examples/rank${i}_confidence-1.1053546667099.sdf`,
          `/examples/rank${i}_confidence-1.3611968755722046.sdf`,
          `/examples/rank${i}_confidence-1.4547926187515259.sdf`,
          `/examples/rank${i}_confidence-1.4845598936080933.sdf`,
          `/examples/rank${i}_confidence-1.5209475755691528.sdf`,
          `/examples/rank${i}_confidence-1.618211269378662.sdf`,
          `/examples/rank${i}_confidence-1.8846811056137085.sdf`,
          `/examples/rank${i}_confidence-1.8951095342636108.sdf`,
          `/examples/rank${i}_confidence-1.9294275045394897.sdf`,
          `/examples/rank${i}_confidence-1.9805632829666138.sdf`,
          `/examples/rank${i}_confidence-2.0869343280792236.sdf`,
          `/examples/rank${i}_confidence-2.1296420097351074.sdf`,
          `/examples/rank${i}_confidence-2.1777448654174805.sdf`,
          `/examples/rank${i}_confidence-2.2822344303131104.sdf`,
          `/examples/rank${i}_confidence-2.4551570415496826.sdf`,
          `/examples/rank${i}_confidence-2.8662607669830322.sdf`,
          `/examples/rank${i}_confidence-3.1361920833587646.sdf`
        ];
        
        // 只添加第i个文件
        if (i <= files.length) {
          ligandUrls.push(files[i - 1]);
        }
      }
      
      // 实际上，我们应该使用真实的文件名
      const realLigandUrls = [
        '/examples/rank1_confidence-0.6142062544822693.sdf',
        '/examples/rank2_confidence-1.0697367191314697.sdf',
        '/examples/rank3_confidence-1.079310417175293.sdf',
        '/examples/rank4_confidence-1.1053546667099.sdf',
        '/examples/rank5_confidence-1.3611968755722046.sdf',
        '/examples/rank6_confidence-1.4547926187515259.sdf',
        '/examples/rank7_confidence-1.4845598936080933.sdf',
        '/examples/rank8_confidence-1.5209475755691528.sdf',
        '/examples/rank9_confidence-1.618211269378662.sdf',
        '/examples/rank10_confidence-1.8846811056137085.sdf',
        '/examples/rank11_confidence-1.8951095342636108.sdf',
        '/examples/rank12_confidence-1.9294275045394897.sdf',
        '/examples/rank13_confidence-1.9805632829666138.sdf',
        '/examples/rank14_confidence-2.0869343280792236.sdf',
        '/examples/rank15_confidence-2.1296420097351074.sdf',
        '/examples/rank16_confidence-2.1777448654174805.sdf',
        '/examples/rank17_confidence-2.2822344303131104.sdf',
        '/examples/rank18_confidence-2.4551570415496826.sdf',
        '/examples/rank19_confidence-2.8662607669830322.sdf',
        '/examples/rank20_confidence-3.1361920833587646.sdf'
      ];
      
      await loadAllPoses(_plugin, realLigandUrls, {
        resetCamera: true,
        colorByRank: true
      });
      
      console.log('所有配体姿态加载完成');
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : String(err);
      console.error('加载所有配体时出错:', errMsg);
      error = `加载所有配体失败: ${errMsg}`;
    } finally {
      loading = false;
    }
  }
</script>

<div class="molecule-viewer-container w-full h-full relative">
  <div 
    bind:this={container} 
    class="molstar-container w-full h-full min-h-[400px] bg-gray-900 rounded-lg overflow-hidden"
  ></div>
  
  {#if loading}
    <div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 z-10">
      <div class="text-white text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
        <div>加载分子结构中...</div>
      </div>
    </div>
  {/if}
  
  {#if error}
    <div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75 z-20">
      <div class="bg-red-900 text-white p-4 rounded-lg max-w-md text-center">
        <h3 class="font-bold mb-2">加载错误</h3>
        <p class="text-sm whitespace-pre-line">{error}</p>
        <button 
          class="mt-3 px-4 py-2 bg-red-700 hover:bg-red-600 rounded text-sm"
          on:click={() => error = null}
        >
          关闭
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .molecule-viewer-container {
    position: relative;
  }
  
  .molstar-container {
    position: relative;
    overflow: hidden;
  }
  
  /* 确保Molstar容器正确显示 */
  :global(.molstar-container .msp-plugin) {
    width: 100% !important;
    height: 100% !important;
  }
</style> 