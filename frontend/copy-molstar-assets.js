#!/usr/bin/env node

// 复制Molstar资源到静态目录脚本
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// 获取当前文件目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 定义源文件和目标目录
const MOLSTAR_CSS = path.resolve(__dirname, 'node_modules/molstar/build/viewer/molstar.css');
const MOLSTAR_JS = path.resolve(__dirname, 'node_modules/molstar/build/viewer/molstar.js');
const IMAGES_DIR = path.resolve(__dirname, 'node_modules/molstar/build/viewer/images');

const TARGET_DIR = path.resolve(__dirname, 'static/vendor/molstar');
const TARGET_IMAGES_DIR = path.resolve(TARGET_DIR, 'images');

// 确保目标目录存在
if (!fs.existsSync(TARGET_DIR)) {
  fs.mkdirSync(TARGET_DIR, { recursive: true });
}

// 复制CSS文件
console.log(`复制CSS: ${MOLSTAR_CSS} -> ${path.join(TARGET_DIR, 'molstar.css')}`);
fs.copyFileSync(MOLSTAR_CSS, path.join(TARGET_DIR, 'molstar.css'));

// 复制JS文件
console.log(`复制JS: ${MOLSTAR_JS} -> ${path.join(TARGET_DIR, 'molstar.js')}`);
fs.copyFileSync(MOLSTAR_JS, path.join(TARGET_DIR, 'molstar.js'));

// 如果有图片目录，复制它
if (fs.existsSync(IMAGES_DIR)) {
  // 确保目标图片目录存在
  if (!fs.existsSync(TARGET_IMAGES_DIR)) {
    fs.mkdirSync(TARGET_IMAGES_DIR, { recursive: true });
  }
  
  // 复制图片
  const images = fs.readdirSync(IMAGES_DIR);
  images.forEach(image => {
    const sourcePath = path.join(IMAGES_DIR, image);
    const targetPath = path.join(TARGET_IMAGES_DIR, image);
    console.log(`复制图片: ${sourcePath} -> ${targetPath}`);
    fs.copyFileSync(sourcePath, targetPath);
  });
}

console.log('Molstar资源复制完成'); 