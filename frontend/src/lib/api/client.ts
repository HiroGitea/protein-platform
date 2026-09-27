// 后端 API 客户端。所有模型推理都是异步任务：提交拿 job_id，再轮询直到终态。

import type {
	DiffDockParams,
	DiffDockResult,
	FoldParams,
	FoldResult,
	GenMolParams,
	GenMolResult,
	HealthResponse,
	Job,
	JobStatus,
	MMseqsParams,
	MMseqsResult,
	MolMimParams,
	MolMimResult,
	UploadResponse
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000';

const TERMINAL: JobStatus[] = ['succeeded', 'failed', 'cancelled'];

export class ApiError extends Error {
	constructor(
		message: string,
		readonly status: number
	) {
		super(message);
		this.name = 'ApiError';
	}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	let res: Response;
	try {
		res = await fetch(`${API_BASE}${path}`, {
			...init,
			headers: { 'Content-Type': 'application/json', ...init?.headers }
		});
	} catch {
		throw new ApiError(`无法连接后端 ${API_BASE}，确认服务已启动`, 0);
	}
	if (!res.ok) {
		const detail = await res.text().catch(() => '');
		throw new ApiError(detail || `${res.status} ${res.statusText}`, res.status);
	}
	return res.json() as Promise<T>;
}

export const getHealth = () => request<HealthResponse>('/api/health');

export const getJob = <T>(id: string) => request<Job<T>>(`/api/jobs/${id}`);

export const cancelJob = (id: string) =>
	request<{ cancelled: boolean }>(`/api/jobs/${id}/cancel`, { method: 'POST' });

export async function uploadFile(file: File): Promise<UploadResponse> {
	const form = new FormData();
	form.append('file', file);
	const res = await fetch(`${API_BASE}/api/files`, { method: 'POST', body: form });
	if (!res.ok) throw new ApiError(await res.text(), res.status);
	return res.json();
}

/** 轮询任务直到终态。onUpdate 每次拿到新状态时回调，方便更新进度条。 */
export async function waitForJob<T>(
	jobId: string,
	onUpdate?: (job: Job<T>) => void,
	options: { intervalMs?: number; timeoutMs?: number; signal?: AbortSignal } = {}
): Promise<Job<T>> {
	const { intervalMs = 1000, timeoutMs = 30 * 60 * 1000, signal } = options;
	const deadline = Date.now() + timeoutMs;

	for (;;) {
		if (signal?.aborted) throw new ApiError('已取消', 0);
		const job = await getJob<T>(jobId);
		onUpdate?.(job);
		if (TERMINAL.includes(job.status)) {
			if (job.status !== 'succeeded') throw new ApiError(job.error ?? `任务${job.status}`, 0);
			return job;
		}
		if (Date.now() > deadline) throw new ApiError('任务超时', 0);
		await new Promise((r) => setTimeout(r, intervalMs));
	}
}

/** 提交 + 等待，一步到位。 */
async function runJob<TResult>(
	path: string,
	body: unknown,
	onUpdate?: (job: Job<TResult>) => void
): Promise<TResult> {
	const { job_id } = await request<{ job_id: string }>(path, {
		method: 'POST',
		body: JSON.stringify(body)
	});
	const job = await waitForJob<TResult>(job_id, onUpdate);
	return job.result as TResult;
}

type OnUpdate<T> = (job: Job<T>) => void;

/** GenMol 分子生成 */
export const generateMolecules = (params: GenMolParams, onUpdate?: OnUpdate<GenMolResult>) =>
	runJob<GenMolResult>('/api/genmol/generate', params, onUpdate);

/** MolMIM 分子性质优化 */
export const optimizeMolecule = (params: MolMimParams, onUpdate?: OnUpdate<MolMimResult>) =>
	runJob<MolMimResult>('/api/molmim/optimize', params, onUpdate);

/** DiffDock 分子对接。protein/ligand 先用 uploadFile 拿 file_id */
export const dockMolecule = (params: DiffDockParams, onUpdate?: OnUpdate<DiffDockResult>) =>
	runJob<DiffDockResult>('/api/diffdock/dock', params, onUpdate);

/** MMseqs2 序列搜索 */
export const searchSequence = (params: MMseqsParams, onUpdate?: OnUpdate<MMseqsResult>) =>
	runJob<MMseqsResult>('/api/mmseqs/search', params, onUpdate);

/** ESMFold 结构预测 */
export const predictStructure = (params: FoldParams, onUpdate?: OnUpdate<FoldResult>) =>
	runJob<FoldResult>('/api/fold/predict', params, onUpdate);

/** 把后端返回的相对路径拼成完整 URL（给 Mol* 或下载链接用） */
export const fileUrl = (path: string) => `${API_BASE}${path}`;
