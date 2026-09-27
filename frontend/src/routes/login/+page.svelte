<script lang="ts">
	import { Mail, Lock, Github, Chrome, Loader2 } from 'lucide-svelte';
	
	let email: string = '';
	let password: string = '';
	let loading: boolean = false;
	let errorMessage: string = '';
	let successMessage: string = '';
	let rememberMe: boolean = false;
	
	async function handleSubmit() {
		loading = true;
		errorMessage = '';
		successMessage = '';
		
		try {
			// 模拟API调用
			await new Promise(resolve => setTimeout(resolve, 1000));
			
			// 简单的验证逻辑
			if (email === 'admin@example.com' && password === 'password') {
				successMessage = '登录成功！正在跳转...';
				setTimeout(() => {
					window.location.href = '/';
				}, 1500);
			} else {
				errorMessage = '邮箱或密码错误，请重试';
			}
		} catch (error) {
			errorMessage = '登录过程中发生错误，请稍后再试';
			console.error('登录错误:', error);
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>用户登录 - 生物信息学平台</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<!-- 头部 -->
		<div class="text-center">
			<h2 class="text-3xl font-bold text-gray-900 dark:text-white">
				用户登录
			</h2>
			<p class="mt-2 text-gray-600 dark:text-gray-400">
				欢迎回来，请登录您的账号
			</p>
		</div>

		<!-- 消息提示 -->
		{#if successMessage}
			<div class="bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg p-4">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
						</svg>
					</div>
					<div class="ml-3">
						<p class="text-sm font-medium text-green-800 dark:text-green-200">
							{successMessage}
						</p>
					</div>
				</div>
			</div>
		{/if}

		{#if errorMessage}
			<div class="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
				<div class="flex items-center">
					<div class="flex-shrink-0">
						<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
						</svg>
					</div>
					<div class="ml-3">
						<p class="text-sm font-medium text-red-800 dark:text-red-200">
							{errorMessage}
						</p>
					</div>
				</div>
			</div>
		{/if}

		<!-- 登录表单 -->
		<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="space-y-4">
				<!-- 邮箱输入 -->
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						邮箱地址
					</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<Mail class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="email"
							type="email"
							bind:value={email}
							required
							class="input pl-10"
							placeholder="请输入邮箱地址"
						/>
					</div>
				</div>

				<!-- 密码输入 -->
				<div>
					<label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						密码
					</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<Lock class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="password"
							type="password"
							bind:value={password}
							required
							class="input pl-10"
							placeholder="请输入密码"
						/>
					</div>
				</div>
			</div>

			<!-- 记住我和忘记密码 -->
			<div class="flex items-center justify-between">
				<div class="flex items-center">
					<input
						id="remember-me"
						type="checkbox"
						bind:checked={rememberMe}
						class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
					/>
					<label for="remember-me" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
						记住我
					</label>
				</div>
				<div class="text-sm">
					<a href="/forgot-password" class="font-medium text-primary-600 hover:text-primary-500">
						忘记密码？
					</a>
				</div>
			</div>

			<!-- 登录按钮 -->
			<div>
				<button
					type="submit"
					disabled={loading}
					class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					{#if loading}
						<Loader2 class="w-5 h-5 mr-2 animate-spin" />
						登录中...
					{:else}
						登录
					{/if}
				</button>
			</div>

			<!-- 社交登录 -->
			<div class="mt-6">
				<div class="relative">
					<div class="absolute inset-0 flex items-center">
						<div class="w-full border-t border-gray-300 dark:border-gray-600" />
					</div>
					<div class="relative flex justify-center text-sm">
						<span class="px-2 bg-gray-50 dark:bg-gray-900 text-gray-500">或者使用以下方式登录</span>
					</div>
				</div>

				<div class="mt-6 grid grid-cols-2 gap-3">
					<button
						type="button"
						class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
					>
						<Github class="h-5 w-5" />
						<span class="ml-2">GitHub</span>
					</button>

					<button
						type="button"
						class="w-full inline-flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
					>
						<Chrome class="h-5 w-5" />
						<span class="ml-2">Google</span>
					</button>
				</div>
			</div>

			<!-- 注册链接 -->
			<div class="text-center">
				<p class="text-sm text-gray-600 dark:text-gray-400">
					还没有账号？
					<a href="/register" class="font-medium text-primary-600 hover:text-primary-500">
						立即注册
					</a>
				</p>
			</div>
		</form>

		<!-- 测试账号提示 -->
		<div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
			<p class="text-sm text-blue-800 dark:text-blue-200">
				<strong>测试账号：</strong><br>
				邮箱：admin@example.com<br>
				密码：password
			</p>
		</div>
	</div>
</div> 