<script lang="ts">
	import { Mail, Lock, User, Loader2 } from 'lucide-svelte';
	
	let formData = {
		name: '',
		email: '',
		password: '',
		confirmPassword: ''
	};
	let loading: boolean = false;
	let errorMessage: string = '';
	let successMessage: string = '';
	let agreeTerms: boolean = false;
	
	async function handleSubmit() {
		loading = true;
		errorMessage = '';
		successMessage = '';
		
		try {
			// 验证密码匹配
			if (formData.password !== formData.confirmPassword) {
				errorMessage = '两次输入的密码不一致';
				return;
			}
			
			// 验证服务条款
			if (!agreeTerms) {
				errorMessage = '请同意服务条款和隐私政策';
				return;
			}
			
			// 模拟API调用
			await new Promise(resolve => setTimeout(resolve, 1500));
			
			successMessage = '注册成功！正在跳转到登录页面...';
			setTimeout(() => {
				window.location.href = '/login';
			}, 2000);
		} catch (error) {
			errorMessage = '注册过程中发生错误，请稍后再试';
			console.error('注册错误:', error);
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>用户注册 - 生物信息学平台</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<!-- 头部 -->
		<div class="text-center">
			<h2 class="text-3xl font-bold text-gray-900 dark:text-white">
				创建账户
			</h2>
			<p class="mt-2 text-gray-600 dark:text-gray-400">
				加入我们的生物信息学平台
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

		<!-- 注册表单 -->
		<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="space-y-4">
				<!-- 姓名输入 -->
				<div>
					<label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						姓名
					</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<User class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="name"
							type="text"
							bind:value={formData.name}
							required
							class="input pl-10"
							placeholder="请输入您的姓名"
						/>
					</div>
				</div>

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
							bind:value={formData.email}
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
							bind:value={formData.password}
							required
							minlength="6"
							class="input pl-10"
							placeholder="请输入密码（至少6位）"
						/>
					</div>
				</div>

				<!-- 确认密码输入 -->
				<div>
					<label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
						确认密码
					</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
							<Lock class="h-5 w-5 text-gray-400" />
						</div>
						<input
							id="confirmPassword"
							type="password"
							bind:value={formData.confirmPassword}
							required
							class="input pl-10"
							placeholder="请再次输入密码"
						/>
					</div>
				</div>
			</div>

			<!-- 服务条款 -->
			<div class="flex items-center">
				<input
					id="agree-terms"
					type="checkbox"
					bind:checked={agreeTerms}
					class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
				/>
				<label for="agree-terms" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
					我同意
					<a href="/terms" class="text-primary-600 hover:text-primary-500">服务条款</a>
					和
					<a href="/privacy" class="text-primary-600 hover:text-primary-500">隐私政策</a>
				</label>
			</div>

			<!-- 注册按钮 -->
			<div>
				<button
					type="submit"
					disabled={loading}
					class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					{#if loading}
						<Loader2 class="w-5 h-5 mr-2 animate-spin" />
						注册中...
					{:else}
						创建账户
					{/if}
				</button>
			</div>

			<!-- 登录链接 -->
			<div class="text-center">
				<p class="text-sm text-gray-600 dark:text-gray-400">
					已有账号？
					<a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
						立即登录
					</a>
				</p>
			</div>
		</form>
	</div>
</div> 