<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import { 
		Home, 
		LogIn, 
		UserPlus, 
		Dna, 
		Search, 
		Atom,
		Menu,
		X,
		Zap,
		Beaker,
		Microscope
	} from 'lucide-svelte';
	
	let sidebarOpen = false;
	
	const navigation = [
		{ name: '首页', href: '/', icon: Home },
		{ name: '登录', href: '/login', icon: LogIn },
		{ name: '注册', href: '/register', icon: UserPlus },
		{ name: 'OpenFold', href: '/openfold', icon: Dna },
		{ name: 'MMseqs2', href: '/mmseq', icon: Search },
		{ name: 'DiffDock', href: '/diffdock', icon: Atom },
		{ name: '分子可视化', href: '/molviewer', icon: Atom },
		{ name: 'GenMol', href: '/genmol', icon: Beaker },
		{ name: 'MolMIM', href: '/molmim', icon: Microscope }
	];
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900">
	<!-- 移动端菜单按钮 -->
	<div class="lg:hidden fixed top-4 left-4 z-50">
		<button
			on:click={() => sidebarOpen = !sidebarOpen}
			class="p-2 rounded-md bg-white dark:bg-gray-800 shadow-lg"
		>
			{#if sidebarOpen}
				<X class="w-6 h-6" />
			{:else}
				<Menu class="w-6 h-6" />
			{/if}
		</button>
	</div>

	<!-- 侧边栏 -->
	<div class="fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out {sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0">
		<div class="flex flex-col h-full">
			<!-- Logo -->
			<div class="flex items-center justify-center h-16 px-4 bg-primary-600">
				<h1 class="text-xl font-bold text-white">生物信息学平台</h1>
			</div>
			
			<!-- 导航菜单 -->
			<nav class="flex-1 px-4 py-6 space-y-2">
				<a
					href="/"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/'}
					class:dark:bg-blue-900={$page.url.pathname === '/'}
					class:text-blue-700={$page.url.pathname === '/'}
					class:dark:text-blue-300={$page.url.pathname === '/'}
				>
					<Home class="w-5 h-5 mr-3" />
					首页
				</a>

				<a
					href="/login"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/login'}
					class:dark:bg-blue-900={$page.url.pathname === '/login'}
					class:text-blue-700={$page.url.pathname === '/login'}
					class:dark:text-blue-300={$page.url.pathname === '/login'}
				>
					<LogIn class="w-5 h-5 mr-3" />
					登录
				</a>

				<a
					href="/register"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/register'}
					class:dark:bg-blue-900={$page.url.pathname === '/register'}
					class:text-blue-700={$page.url.pathname === '/register'}
					class:dark:text-blue-300={$page.url.pathname === '/register'}
				>
					<UserPlus class="w-5 h-5 mr-3" />
					注册
				</a>

				<div class="border-t border-gray-200 dark:border-gray-700 my-4"></div>

				<a
					href="/openfold"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/openfold'}
					class:dark:bg-blue-900={$page.url.pathname === '/openfold'}
					class:text-blue-700={$page.url.pathname === '/openfold'}
					class:dark:text-blue-300={$page.url.pathname === '/openfold'}
				>
					<Dna class="w-5 h-5 mr-3" />
					OpenFold
				</a>

				<a
					href="/mmseq"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/mmseq'}
					class:dark:bg-blue-900={$page.url.pathname === '/mmseq'}
					class:text-blue-700={$page.url.pathname === '/mmseq'}
					class:dark:text-blue-300={$page.url.pathname === '/mmseq'}
				>
					<Search class="w-5 h-5 mr-3" />
					MMseqs2
				</a>

				<a
					href="/diffdock"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/diffdock'}
					class:dark:bg-blue-900={$page.url.pathname === '/diffdock'}
					class:text-blue-700={$page.url.pathname === '/diffdock'}
					class:dark:text-blue-300={$page.url.pathname === '/diffdock'}
				>
					<Zap class="w-5 h-5 mr-3" />
					DiffDock
				</a>

				<a
					href="/molviewer"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/molviewer'}
					class:dark:bg-blue-900={$page.url.pathname === '/molviewer'}
					class:text-blue-700={$page.url.pathname === '/molviewer'}
					class:dark:text-blue-300={$page.url.pathname === '/molviewer'}
				>
					<Atom class="w-5 h-5 mr-3" />
					分子可视化
				</a>

				<a
					href="/genmol"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/genmol'}
					class:dark:bg-blue-900={$page.url.pathname === '/genmol'}
					class:text-blue-700={$page.url.pathname === '/genmol'}
					class:dark:text-blue-300={$page.url.pathname === '/genmol'}
				>
					<Beaker class="w-5 h-5 mr-3" />
					GenMol
				</a>

				<a
					href="/molmim"
					class="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
					class:bg-blue-50={$page.url.pathname === '/molmim'}
					class:dark:bg-blue-900={$page.url.pathname === '/molmim'}
					class:text-blue-700={$page.url.pathname === '/molmim'}
					class:dark:text-blue-300={$page.url.pathname === '/molmim'}
				>
					<Microscope class="w-5 h-5 mr-3" />
					MolMIM
				</a>
			</nav>
		</div>
	</div>

	<!-- 主内容区域 -->
	<div class="lg:ml-64">
		<main class="p-6">
			<slot />
		</main>
	</div>
</div>

<!-- 移动端遮罩 -->
{#if sidebarOpen}
	<div 
		class="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
		on:click={() => sidebarOpen = false}
		on:keydown={(e) => e.key === 'Escape' && (sidebarOpen = false)}
		role="button"
		tabindex="0"
	></div>
{/if} 