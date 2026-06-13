import {
  AuthenticationError,
  AuthorizationError,
  ConnectionError,
  EnmaskError,
  NotFoundError,
  RateLimitError,
  ServerError,
  ValidationError,
} from "./errors";
import type {
  AuthResponse,
  ComplianceReport,
  Connection,
  MaskingJob,
  MaskingRule,
  ScanResult,
  SummaryReport,
} from "./types";

interface RequestConfig {
  method: string;
  path: string;
  body?: Record<string, unknown>;
  params?: Record<string, string>;
}

export class EnmaskClient {
  private baseUrl: string;
  private apiKey?: string;
  private token?: string;
  private timeout: number;

  constructor(baseUrl: string, apiKey?: string, token?: string, timeout = 30000) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
    this.token = token;
    this.timeout = timeout;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) headers["X-API-Key"] = this.apiKey;
    if (this.token) headers["Authorization"] = `Bearer ${this.token}`;
    return headers;
  }

  private setToken(token: string): void {
    this.token = token;
  }

  private async request<T>(config: RequestConfig): Promise<T> {
    const { method, path, body, params } = config;
    let url = `${this.baseUrl}${path}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      const response = await fetch(url, {
        method,
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      await this.handleErrors(response);
      const text = await response.text();
      return text ? JSON.parse(text) : (undefined as T);
    } catch (error) {
      if (error instanceof EnmaskError) throw error;
      throw new ConnectionError(`Request failed: ${error}`);
    }
  }

  private async handleErrors(response: Response): Promise<void> {
    if (response.ok) return;
    const status = response.status;
    let detail: string;
    try {
      const body = await response.json();
      detail = body.detail || response.statusText;
    } catch {
      detail = response.statusText;
    }
    if (status === 401) throw new AuthenticationError(detail);
    if (status === 403) throw new AuthorizationError(detail);
    if (status === 404) throw new NotFoundError(detail);
    if (status === 422) throw new ValidationError(detail);
    if (status === 429) throw new RateLimitError(detail);
    if (status >= 500) throw new ServerError(detail);
    throw new EnmaskError(detail, status);
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const data = await this.request<AuthResponse>({
      method: "POST",
      path: "/api/v2/auth/login",
      body: { email, password },
    });
    this.setToken(data.access_token);
    return data;
  }

  async loginGoogle(idToken: string): Promise<AuthResponse> {
    const data = await this.request<AuthResponse>({
      method: "POST",
      path: "/api/v2/auth/google",
      body: { id_token: idToken },
    });
    this.setToken(data.access_token);
    return data;
  }

  async listConnections(): Promise<Connection[]> {
    return this.request<Connection[]>({ method: "GET", path: "/api/v2/connections" });
  }

  async createConnection(data: Record<string, unknown>): Promise<Connection> {
    return this.request<Connection>({
      method: "POST",
      path: "/api/v2/connections",
      body: data,
    });
  }

  async deleteConnection(id: string): Promise<void> {
    await this.request<void>({ method: "DELETE", path: `/api/v2/connections/${id}` });
  }

  async testConnection(id: string): Promise<boolean> {
    const result = await this.request<{ success: boolean }>({
      method: "POST",
      path: `/api/v2/connections/${id}/test`,
    });
    return result.success;
  }

  async discoverPii(id: string): Promise<Record<string, unknown>[]> {
    return this.request<Record<string, unknown>[]>({
      method: "POST",
      path: `/api/v2/connections/${id}/discover`,
    });
  }

  async listRules(): Promise<MaskingRule[]> {
    return this.request<MaskingRule[]>({ method: "GET", path: "/api/v2/rules" });
  }

  async createRule(data: Record<string, unknown>): Promise<MaskingRule> {
    return this.request<MaskingRule>({ method: "POST", path: "/api/v2/rules", body: data });
  }

  async updateRule(id: string, data: Record<string, unknown>): Promise<MaskingRule> {
    return this.request<MaskingRule>({
      method: "PUT",
      path: `/api/v2/rules/${id}`,
      body: data,
    });
  }

  async deleteRule(id: string): Promise<void> {
    await this.request<void>({ method: "DELETE", path: `/api/v2/rules/${id}` });
  }

  async listJobs(): Promise<MaskingJob[]> {
    return this.request<MaskingJob[]>({ method: "GET", path: "/api/v2/jobs" });
  }

  async createJob(data: Record<string, unknown>): Promise<MaskingJob> {
    return this.request<MaskingJob>({ method: "POST", path: "/api/v2/jobs", body: data });
  }

  async runJob(id: string): Promise<void> {
    await this.request<void>({ method: "POST", path: `/api/v2/jobs/${id}/run` });
  }

  async unmaskJob(id: string): Promise<void> {
    await this.request<void>({ method: "POST", path: `/api/v2/jobs/${id}/unmask` });
  }

  async getJobStatus(id: string): Promise<MaskingJob> {
    return this.request<MaskingJob>({ method: "GET", path: `/api/v2/jobs/${id}` });
  }

  async shareJob(id: string, email: string): Promise<void> {
    await this.request<void>({
      method: "POST",
      path: `/api/v2/jobs/${id}/share`,
      body: { email },
    });
  }

  async getSummary(): Promise<SummaryReport> {
    return this.request<SummaryReport>({ method: "GET", path: "/api/v2/reports/summary" });
  }

  async getComplianceReport(framework: string): Promise<ComplianceReport> {
    return this.request<ComplianceReport>({
      method: "GET",
      path: `/api/v2/reports/compliance/${framework}`,
    });
  }

  async scanDatabase(connectionId: string): Promise<ScanResult> {
    return this.request<ScanResult>({
      method: "POST",
      path: "/api/v2/discovery/scan",
      body: { connection_id: connectionId },
    });
  }

  async getScanResults(scanId: string): Promise<ScanResult> {
    return this.request<ScanResult>({
      method: "GET",
      path: `/api/v2/discovery/scans/${scanId}`,
    });
  }
}
