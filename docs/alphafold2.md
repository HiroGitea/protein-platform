# AlphaFold 2

The `/api/fold/predict` endpoint runs AlphaFold 2 through an independently deployed NVIDIA NIM service. The platform handles job submission, bounded polling, and downloadable PDB outputs. Model execution and MSA databases live in the NIM deployment; no folding model is loaded into the FastAPI process.

NVIDIA marks the [public AlphaFold 2 endpoint as deprecated](https://build.nvidia.com/deepmind/alphafold2). There is no default public endpoint. Configure a local or remote NIM deployment explicitly.

## Deploy and configure

Follow NVIDIA's [prerequisites](https://docs.nvidia.com/nim/bionemo/alphafold2/latest/prerequisites.html) and [deployment guide](https://docs.nvidia.com/nim/bionemo/alphafold2/latest/quickstart-guide.html) to provision the GPU runtime, model assets, databases, and registry credentials. When running NIM on the same machine, publish its container port 8000 on **host port 8001** (`-p 8001:8000`) to avoid the platform backend's port 8000.

NVIDIA lists a minimum of 32 GB GPU memory and 1,250 GB free storage for this NIM deployment, plus 64 GB RAM and 24 CPU cores. The project’s documented 16 GB development GPU does not meet that minimum; use a suitable separate server. See the linked prerequisites for current requirements.

Wait for `http://127.0.0.1:8001/v1/health/ready` to report readiness, then set these values in `backend/.env`:

```dotenv
PROTEIN_FOLD_PROVIDER=local
PROTEIN_AF2_LOCAL_URL=http://127.0.0.1:8001
PROTEIN_AF2_TIMEOUT_SECONDS=7200
```

For a remote deployment:

```dotenv
PROTEIN_FOLD_PROVIDER=remote
PROTEIN_AF2_REMOTE_URL=https://your-af2-service.example
PROTEIN_AF2_API_KEY=your-service-token
```

`PROTEIN_AF2_API_KEY` is optional and sent only to the remote provider as a Bearer token. It is separate from `NVIDIA_API_KEY`. URLs specify the base before `/protein-structure/alphafold2/predict-structure-from-sequence`; include any gateway prefix in the base URL.

Restart the backend after changes. `/api/health` checks whether the AF2 provider's address is configured; it does **not** probe NIM readiness. With `auto`, a configured local URL is preferred over a configured remote URL. Inference failures do not trigger automatic remote retries.

The old `uv sync --group fold` dependency group has been removed. AF2 dependencies are managed by the NIM deployment.

## Submit a prediction

```bash
curl -X POST http://127.0.0.1:8000/api/fold/predict \
  -H 'Content-Type: application/json' \
  -d '{"sequence":"MKTAYIAKQRQISFVKSHFS","algorithm":"jackhmmer","relax_prediction":true}'
```

The sequence must contain 1–4096 standard amino acids. Lowercase and whitespace are normalized; FASTA headers, gaps, and ambiguous residue symbols are rejected. Optional `algorithm` accepts `jackhmmer` (default) or `mmseqs2`; `relax_prediction` defaults to `true`.

Poll `/api/jobs/{job_id}` until it reaches a terminal status. Successful results preserve `pdb_file` and `viewer_url` for existing clients, and add `model: "alphafold2"` and `pdb_files`. Every returned structure is available as a job file: `predicted.pdb`, `predicted_2.pdb`, and so on, in service response order. The first file is used for the viewer; the platform does not independently rank models.

The adapter follows the [NVIDIA API contract](https://docs.api.nvidia.com/nim/reference/deepmind-alphafold2-infer): a JSON array of PDB strings, with optional HTTP 202 / `nvcf-reqid` polling at `{base_url}/status/{request_id}`. `PROTEIN_AF2_TIMEOUT_SECONDS` bounds the whole request, including polling; `PROTEIN_AF2_POLL_INTERVAL_SECONDS` defaults to 5. Cancelling a platform job stops waiting, but does not cancel computation already running on the NIM server.

## Validation

Automated tests use a simulated NIM service to cover request validation, both providers, asynchronous responses, authentication, timeouts, cancellation, malformed responses, and the complete job-to-download flow. Actual GPU inference requires a configured deployment and is not exercised by these tests.
