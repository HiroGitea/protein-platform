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

export type ProviderKind = 'local' | 'remote';

export interface ProviderStatus {
	kind: ProviderKind;
	available: boolean;
	reason: string;
	note: string;
	details: Record<string, unknown>;
}

export interface EngineStatus {
	name: string;
	available: boolean;
	/** 配置的偏好：auto / local / remote */
	preference: string;
	/** 当前实际会用哪个 provider，null 表示都不可用 */
	active: ProviderKind | null;
	reason: string;
	providers: ProviderStatus[];
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

export interface MolMimParams {
	smiles: string;
	algorithm?: 'CMA-ES' | 'none';
	num_molecules?: number;
	property_name?: 'QED' | 'plogP';
	minimize?: boolean;
	iterations?: number;
	particles?: number;
	min_similarity?: number;
	scaled_radius?: number;
}

export interface MolMimResult extends GenMolResult {
	input_smiles: string;
	optimized_property: string;
	best?: GeneratedMolecule;
}

export interface DiffDockParams {
	protein_file_id: string;
	ligand_file_id: string;
	num_poses?: number;
	steps?: number;
	time_divisions?: number;
	save_trajectory?: boolean;
}

export interface DockedPose {
	rank: number | null;
	confidence: number | null;
	file: string;
}

export interface DiffDockResult {
	poses: DockedPose[];
	num_poses: number;
	protein_file?: string;
}

export interface MMseqsParams {
	sequence?: string;
	file_id?: string;
	database?: string;
	sensitivity?: number;
	max_hits?: number;
}

export interface SequenceHit {
	target: string;
	identity: number;
	alignment_length: number;
	evalue: string;
	bit_score: number;
}

export interface MMseqsResult {
	database: string;
	hits: SequenceHit[];
}

export interface FoldParams {
	sequence: string;
}

export interface FoldResult {
	sequence_length: number;
	pdb_file: string;
	/** 直接丢给 Mol* 加载 */
	viewer_url: string;
}
