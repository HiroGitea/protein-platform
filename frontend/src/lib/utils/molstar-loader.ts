/**
 * Molstar加载器 - 精简版
 */

// 导入类型
import type { PluginUIContext } from 'molstar/lib/mol-plugin-ui/context';
import { createPluginUI } from 'molstar/lib/mol-plugin-ui';
import { DefaultPluginUISpec } from 'molstar/lib/mol-plugin-ui/spec';
import { Color } from 'molstar/lib/mol-util/color';

// 将CDN版本的molstar复制到静态目录
export const molstarCssUrl = '/vendor/molstar/molstar.css';

// 声明全局molstar变量类型
declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    molstar?: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      PluginContext: any; // 核心插件上下文对象
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      Viewer: any;        // 查看器实例
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      DefaultPluginUISpec: any; // 默认UI规格
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      PluginConfig: any;  // 插件配置
      // 其他需要的Molstar类型
    }; 
  }
}

// 创建插件实例
export async function createMolstarPlugin(
  container: HTMLElement
): Promise<PluginUIContext | undefined> {
  try {
    console.log('开始创建Mol*插件...');
    console.log('容器尺寸:', {
      width: container.clientWidth,
      height: container.clientHeight,
      offsetWidth: container.offsetWidth,
      offsetHeight: container.offsetHeight
    });
    
    // 确保容器有尺寸和可见性
    container.style.visibility = 'visible';
    container.style.display = 'block';
    
    if (container.clientWidth === 0 || container.clientHeight === 0) {
      console.warn('Mol*容器尺寸为0，设置默认尺寸');
      container.style.width = '100%';
      container.style.height = '100%';
      container.style.minHeight = '400px';
      
      // 强制浏览器重新计算布局
      void container.offsetHeight;
      
      console.log('设置尺寸后的容器大小:', {
        width: container.clientWidth,
        height: container.clientHeight
      });
      
      // 如果仍然为0，可能是容器被隐藏了，增加额外设置
      if (container.clientWidth === 0 || container.clientHeight === 0) {
        container.style.position = 'relative';
        container.style.minWidth = '600px';
        document.body.appendChild(container);
        console.log('紧急措施：将容器附加到body，尺寸:', {
          width: container.clientWidth,
          height: container.clientHeight
        });
      }
    }
    
    // 创建加载指示器
    const loadingIndicator = document.createElement('div');
    loadingIndicator.style.position = 'absolute';
    loadingIndicator.style.top = '50%';
    loadingIndicator.style.left = '50%';
    loadingIndicator.style.transform = 'translate(-50%, -50%)';
    loadingIndicator.style.color = 'white';
    loadingIndicator.style.fontSize = '14px';
    loadingIndicator.style.zIndex = '1000';
    loadingIndicator.textContent = '加载Mol*中...';
    container.appendChild(loadingIndicator);
    
    try {
      // 检查 molstar.js 和 molstar.css 是否加载
      console.log('检查Mol*资源是否已加载...');
      const molstarJsReady = typeof window.molstar !== 'undefined';
      
      if (!molstarJsReady) {
        console.warn('Mol* JavaScript库似乎未加载，将尝试动态加载');
        // 尝试动态加载molstar.js
        await loadMolstarResources();
      }
      
      // 初始化Mol*插件
      console.log('正在初始化Mol*插件...');
      
      // 在初始化前暂时抑制React警告
      const originalConsoleWarn = console.warn;
      console.warn = (message, ...args) => {
        if (typeof message === 'string' && 
            (message.includes('ReactDOM.render') || 
             message.includes('createRoot'))) {
          return;
        }
        originalConsoleWarn(message, ...args);
      };
      
      // 配置插件界面
      const spec = {
        ...DefaultPluginUISpec(),
        layout: {
          initial: {
            isExpanded: false,
            showControls: true
          }
        },
        components: {
          ...DefaultPluginUISpec().components,
          remoteState: 'none' as const
        }
      };
      
      // 创建插件 - 添加超时处理
      console.log('调用createPluginUI...');
      let plugin: PluginUIContext | undefined = undefined;
      
      try {
        // 添加超时保护
        const pluginPromise = createPluginUI(container, spec);
        const timeoutPromise = new Promise<PluginUIContext>((_, reject) => {
          setTimeout(() => reject(new Error('创建Mol*插件超时(10秒)')), 10000);
        });
        
        plugin = await Promise.race([pluginPromise, timeoutPromise]);
        console.log('Mol*插件创建成功');
      } catch (timeoutErr) {
        console.error('创建插件时出错或超时:', timeoutErr);
        throw new Error(`Mol*插件创建失败: ${timeoutErr instanceof Error ? timeoutErr.message : String(timeoutErr)}`);
      }
      
      // 恢复原来的console.warn
      console.warn = originalConsoleWarn;
      
      // 移除加载指示器
      if (loadingIndicator.parentNode) {
        loadingIndicator.parentNode.removeChild(loadingIndicator);
      }
      
      return plugin;
    } catch (err) {
      // 处理错误
      if (loadingIndicator.parentNode) {
        loadingIndicator.parentNode.removeChild(loadingIndicator);
      }
      
      const errorMessage = err instanceof Error ? err.message : String(err);
      console.error('创建Mol*插件失败:', errorMessage);
      
      const errorIndicator = document.createElement('div');
      errorIndicator.style.position = 'absolute';
      errorIndicator.style.top = '50%';
      errorIndicator.style.left = '50%';
      errorIndicator.style.transform = 'translate(-50%, -50%)';
      errorIndicator.style.color = '#ff6666';
      errorIndicator.style.fontSize = '14px';
      errorIndicator.style.textAlign = 'center';
      errorIndicator.style.maxWidth = '80%';
      errorIndicator.style.zIndex = '1000';
      errorIndicator.style.padding = '10px';
      errorIndicator.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
      errorIndicator.style.borderRadius = '4px';
      errorIndicator.innerHTML = `Mol*加载失败:<br>${errorMessage}`;
      container.appendChild(errorIndicator);
      
      throw err;
    }
  } catch (error) {
    console.error('创建Molstar插件时出错:', error);
    return undefined;
  }
}

// 动态加载Molstar资源
async function loadMolstarResources(): Promise<void> {
  return new Promise((resolve, reject) => {
    // 加载CSS
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = '/vendor/molstar/molstar.css';
    document.head.appendChild(cssLink);
    
    // 加载JS
    const script = document.createElement('script');
    script.src = '/vendor/molstar/molstar.js';
    script.async = true;
    
    script.onload = () => {
      console.log('Mol*资源动态加载成功');
      resolve();
    };
    
    script.onerror = () => {
      console.error('动态加载Mol*资源失败');
      reject(new Error('无法加载Mol*资源'));
    };
    
    document.head.appendChild(script);
  });
}

// 获取文件格式
export function getFormatFromFile(file: File): string {
  const extension = file.name.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdb': return 'pdb';
    case 'sdf': return 'sdf';
    case 'mol': return 'mol';
    case 'mol2': return 'mol2';
    case 'cif': return 'mmcif';
    default: return 'pdb';
  }
}

// 加载结构文件
export async function loadStructureFromFile(
  plugin: PluginUIContext,
  file: File,
  representationType: 'cartoon' | 'ball-and-stick' = 'cartoon'
): Promise<void> {
  const format = getFormatFromFile(file) as 'pdb' | 'sdf' | 'mol' | 'mol2' | 'mmcif';
  
  // 重试机制
  let attempts = 0;
  const maxAttempts = 3;
  
  async function attemptLoad(): Promise<void> {
    attempts++;
    
    try {
      console.log(`尝试加载文件 ${file.name} (第${attempts}次尝试)`);
      
      // 读取文件内容
      const fileContent = await file.text();
      
      if (!fileContent || fileContent.trim().length === 0) {
        throw new Error('文件内容为空');
      }
      
      console.log(`文件内容长度: ${fileContent.length} 字符`);
      
      // 创建数据源
      const data = await plugin.builders.data.rawData({
        data: fileContent,
        label: file.name
      });
      
      // 解析轨迹
      const trajectory = await plugin.builders.structure.parseTrajectory(data, format);
      
      // 创建模型
      const model = await plugin.builders.structure.createModel(trajectory);
      
      // 创建结构
      const structure = await plugin.builders.structure.createStructure(model);
      
      // 应用表示
      if (representationType === 'cartoon') {
        await plugin.builders.structure.representation.addRepresentation(structure, {
          type: 'cartoon',
          color: 'chain-id'
        });
      } else if (representationType === 'ball-and-stick') {
        await plugin.builders.structure.representation.addRepresentation(structure, {
          type: 'ball-and-stick',
          color: 'element-symbol'
        });
      }
      
      console.log(`文件 ${file.name} 加载成功`);
    } catch (error) {
      console.error(`加载文件失败 (第${attempts}次尝试):`, error);
      
      if (attempts < maxAttempts) {
        console.log(`将在1秒后重试...`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        return attemptLoad();
      } else {
        throw error;
      }
    }
  }
  
  await attemptLoad();
}

// 专门加载SDF文件的方法
export async function loadSdfFile(
  plugin: PluginUIContext,
  file: File
): Promise<void> {
  try {
    console.log(`加载SDF文件: ${file.name}`);
    
    // 读取文件内容
    const fileContent = await file.text();
    
    if (!fileContent || fileContent.trim().length === 0) {
      throw new Error('SDF文件内容为空');
    }
    
    // 创建数据源
    const data = await plugin.builders.data.rawData({
      data: fileContent,
      label: file.name
    });
    
    // 解析为SDF格式
    const trajectory = await plugin.builders.structure.parseTrajectory(data, 'sdf');
    
    // 创建模型
    const model = await plugin.builders.structure.createModel(trajectory);
    
    // 创建结构
    const structure = await plugin.builders.structure.createStructure(model);
    
    // 应用球棍模型表示
    await plugin.builders.structure.representation.addRepresentation(structure, {
      type: 'ball-and-stick',
      color: 'element-symbol'
    });
    
    console.log(`SDF文件 ${file.name} 加载成功`);
  } catch (error) {
    console.error('加载SDF文件失败:', error);
    throw error;
  }
}

/**
 * 实现"查看所有姿态"功能：同时显示多个SDF配体文件
 * @param plugin Mol*插件实例
 * @param ligandUrls 多个配体文件的URL数组
 * @param options 选项
 */
export async function loadAllPoses(
  plugin: PluginUIContext,
  ligandUrls: string[],
  options?: {
    resetCamera?: boolean;
    colorByRank?: boolean; // 是否按排名上色
  }
): Promise<void> {
  if (!ligandUrls.length) {
    console.warn('没有提供配体文件URL');
    return;
  }
  
  console.log(`同时加载${ligandUrls.length}个姿态...`);
  
  // 固定使用的蛋白质PDB路径
  const proteinUrl = '/examples/target_protein.pdb';
  
  // 清除所有现有结构
  await plugin.clear();
  
  // 第一步：加载蛋白质结构
  console.log(`加载蛋白质文件: ${proteinUrl}`);
  try {
    const pdbData = await plugin.builders.data.download({ url: proteinUrl });
    const pdbTrajectory = await plugin.builders.structure.parseTrajectory(pdbData, 'pdb');
    
    // 使用默认设置显示蛋白质
    await plugin.builders.structure.hierarchy.applyPreset(pdbTrajectory, 'default');
    console.log('蛋白质加载成功');
  } catch (err) {
    console.error('加载蛋白质失败:', err);
    // 继续尝试加载配体
  }
  
  // 第二步：逐个加载所有配体，并使用不同颜色
  console.log(`开始加载${ligandUrls.length}个配体文件...`);
  
  const colors = [
    // 丰富多彩的配色方案
    [1, 0, 0],         // 红
    [0, 1, 0],         // 绿
    [0, 0, 1],         // 蓝
    [1, 1, 0],         // 黄
    [1, 0, 1],         // 紫红
    [0, 1, 1],         // 青
    [1, 0.5, 0],       // 橙
    [0.5, 0, 1],       // 紫
    [0, 0.5, 1],       // 天蓝
    [0.5, 1, 0],       // 黄绿
    [1, 0, 0.5],       // 粉红
    [0.5, 0.5, 1],     // 淡紫
    [0.8, 0.8, 0.8],   // 灰
    [0.3, 0.8, 0.3],   // 深绿
    [0.8, 0.3, 0.3],   // 深红
    [0.3, 0.3, 0.8],   // 深蓝
    [0.8, 0.8, 0.3],   // 深黄
    [0.3, 0.8, 0.8],   // 深青
    [0.8, 0.3, 0.8],   // 深紫
    [0.5, 0.5, 0.5]    // 中灰
  ];
  
  // 使用dataTransaction包裹多个加载操作，提高效率
  await plugin.dataTransaction(async () => {
    for (let i = 0; i < ligandUrls.length; i++) {
      const url = ligandUrls[i];
      const rank = i + 1; // 排名从1开始计算
      
      try {
        console.log(`加载配体文件 ${rank}/${ligandUrls.length}: ${url}`);
        
        // 加载SDF数据
        const sdfData = await plugin.builders.data.download({ url });
        const sdfTrajectory = await plugin.builders.structure.parseTrajectory(sdfData, 'sdf');
        
        // 使用默认设置显示配体
        await plugin.builders.structure.hierarchy.applyPreset(sdfTrajectory, 'default');
        
        console.log(`配体${rank}加载成功`);
      } catch (err) {
        console.error(`加载配体${rank}失败:`, err);
        // 继续加载下一个配体
      }
    }
  });
  
  console.log(`所有${ligandUrls.length}个姿态加载完成`);
  
  // 重置相机视图以显示所有结构
  if (options?.resetCamera !== false && plugin.canvas3d) {
    plugin.canvas3d.requestCameraReset();
  }
} 