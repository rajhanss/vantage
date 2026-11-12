# VANTAGE — Security, Privacy & Data Governance

## 1. Threat Model & Security Principles

Vantage is an intelligence system that ingests untrusted text, code, and metadata from external platforms. The primary threat vectors are:
1. **Prompt Injection & Indirect Jailbreaks**: Malicious instructions embedded inside retrieved GitHub READMEs, discussion posts, or articles attempting to hijack agent synthesis.
2. **Denial of Service via Unbounded Ingestion**: Rate-limit exhaustion or memory blowouts from external data feeds.
3. **Secret Leakage**: Exposure of external provider API keys or database credentials in client bundles or public git commits.

---

## 2. Security Controls

### 2.1 Untrusted Content Isolation
- External text (e.g. scraped comments, markdown files) is treated strictly as **untrusted data payloads**.
- In agent prompts, external data is enclosed in dedicated XML boundary tags (`<untrusted_source_content>...</untrusted_source_content>`) with strict system prompt directives instructing the model never to follow instructions found within those tags.

### 2.2 Secret Protection & Zero-Push Mandate
- No API keys or tokens are ever hardcoded in source code or committed to Git.
- All secrets are loaded through environment variables validated by Pydantic `BaseSettings`.
- `.gitignore` strictly blocks `.env`, `*.key`, and secret tokens.

### 2.3 Rate Limiting & Safe Acquisition
- Ingestion adapters enforce exponential backoff with jitter on HTTP `429 Too Many Requests`.
- Respects upstream `Retry-After` headers and platform rate limits.
- Public read-only endpoints are accessed without spoofing or unauthorized bypasses.
