// 与后端 app/schemas.py 一一对应，改后端记得同步这里。

export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled';

export interface JobFile {
	name: string;
	size: number;
	url: string;
}

export interface Job<T = unknown> {
	id: string;
	engine: string;
	status: JobStatus;
	progress: number;
	message: string;
	created_at: string;
	started_at: string | null;
	finished_at: string | null;
	params: Record<string, unknown>;
	result: T | null;
	files: JobFile[];
	error: string | null;
}

export interface EngineStatus {
	name: string;
	available: boolean;
	reason: string;
	checkpoint_present: boolean;
	details: Record<string, unknown>;
}

export interface GpuInfo {
	available: boolean;
	name: string | null;
	driver_version: string | null;
	memory_total_mb: number | null;
	memory_used_mb: number | null;
	compute_capability: string | null;
	torch_version: string | null;
	reason: string;
}

export interface HealthResponse {
	status: 'ok';
	gpu: GpuInfo;
	engines: EngineStatus[];
}

export interface UploadResponse {
	file_id: string;
	filename: string;
	size: number;
}

// ---- 各工具的参数与结果 ----

export interface GenMolParams {
	mode?: 'denovo' | 'fragment_completion' | 'fragment_linking';
	smiles?: string;
	num_samples?: number;
	softmax_temp?: number;
	randomness?: number;
	min_add_len?: number;
}

export interface GeneratedMolecule {
	smiles: string;
	qed: number;
	mol_weight: number;
	logp: number;
	num_atoms: number;
}

export interface GenMolResult {
	molecules: GeneratedMolecule[];
	requested: number;
	generated: number;
	valid: number;
	validity: number;
	unique: number;
}
