import type {
  Connection, ConnectionCreate, ConnectionTestResult,
  MaskingRule, RuleCreate,
  MaskingJob, JobCreate,
  Summary, User, AuthResponse, DynamicQueryResponse,
  AuditLogEntry, PaginatedResponse, PaginationParams,
  DiscoveryScan, DiscoveryResult, ScanConfig,
  Schedule, ScheduleCreate, ScheduleHistory,
  Plugin, ApiKey, NotificationPreference,
  ComplianceReport, ExportFormat,
  ShareJobRequest, ApiError,
} from '../types';

export const RESOLVED_API_BASE =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://127.0.0.1:8000/api/v1' : '/api/v1');

const BASE = RESOLVED_API_BASE;
const TOKEN_KEY = 'enmask_access_token';
const REFRESH_TOKEN_KEY = 'enmask_refresh_token';
const MAX_RETRIES = 2;
const RETRY_DELAY = 1000;

const activeControllers = new Map<string, AbortController>();

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setStoredRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

function buildQueryString(params: Record<string, unknown>): string {
  const entries = Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '');
  if (entries.length === 0) return '';
  return '?' + entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&');
}

export function cancelRequest(requestId: string): void {
  const controller = activeControllers.get(requestId);
  if (controller) {
    controller.abort();
    activeControllers.delete(requestId);
  }
}

async function refreshTokenIfNeeded(): Promise<boolean> {
  const refreshToken = getStoredRefreshToken();
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const data: AuthResponse = await res.json();
    setStoredToken(data.access_token);
    if (data.refresh_token) setStoredRefreshToken(data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

function parseError(res: Response, body: unknown): ApiError {
  const detail = (body as Record<string, unknown>)?.detail;
  let message: string;
  if (typeof detail === 'string') {
    message = detail;
  } else if (Array.isArray(detail)) {
    message = detail.map((d: { msg?: string }) => d.msg ?? '').filter(Boolean).join('; ') || 'Request failed';
  } else {
    message = res.statusText || 'Request failed';
  }
  return {
    status: res.status,
    message,
    detail: detail as string | Record<string, unknown>[],
    timestamp: new Date().toISOString(),
  };
}

async function request<T>(
  path: string,
  init?: RequestInit & { retries?: number; requestId?: string },
): Promise<T> {
  const retries = init?.retries ?? MAX_RETRIES;
  const requestId = init?.requestId;
  const token = getStoredToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string> || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let controller: AbortController | undefined;
  if (requestId) {
    controller = new AbortController();
    activeControllers.set(requestId, controller);
  }

  const url = `${BASE}${path}`;
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, {
        ...init,
        headers,
        signal: controller?.signal,
      });

      if (res.status === 401 && attempt === 0) {
        const refreshed = await refreshTokenIfNeeded();
        if (refreshed) {
          headers.Authorization = `Bearer ${getStoredToken()}`;
          continue;
        }
        clearStoredToken();
        window.location.href = '/login';
        throw new Error('Session expired');
      }

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw parseError(res, body);
      }

      if (res.status === 204) return undefined as unknown as T;
      return res.json();
    } catch (e) {
      lastError = e as Error;
      if ((e as Error).name === 'AbortError') throw e;
      if (attempt < retries && !(e as ApiError).status) {
        await new Promise(r => setTimeout(r, RETRY_DELAY * (attempt + 1)));
        continue;
      }
      throw e;
    }
  } finally {
    if (requestId) activeControllers.delete(requestId);
  }

  throw lastError || new Error('Request failed');
}

function queryParams(params: PaginationParams): string {
  return buildQueryString(params as Record<string, unknown>);
}

// ---- Auth ----
export const authApi = {
  register: (email: string, password: string, name: string) =>
    request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    }),
  login: (email: string, password: string) =>
    request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  loginGoogle: (idToken: string) =>
    request<AuthResponse>('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ id_token: idToken }),
    }),
  me: () => request<User>('/auth/me'),
  refresh: (refreshToken: string) =>
    request<AuthResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),
  changePassword: (oldPassword: string, newPassword: string) =>
    request<{ message: string }>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    }),
  enableMfa: () => request<{ secret: string; qr_url: string }>('/auth/mfa/enable', { method: 'POST' }),
  verifyMfa: (code: string) =>
    request<{ message: string }>('/auth/mfa/verify', {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),
  disableMfa: (code: string) =>
    request<{ message: string }>('/auth/mfa/disable', {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),
};

// ---- Connections ----
export const connectionsApi = {
  list: (params?: PaginationParams) =>
    request<PaginatedResponse<Connection>>(`/connections/${queryParams(params || {})}`),
  listAll: () => request<Connection[]>('/connections/'),
  get: (id: string) => request<Connection>(`/connections/${id}`),
  create: (data: ConnectionCreate) =>
    request<Connection>('/connections/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ConnectionCreate>) =>
    request<Connection>(`/connections/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/connections/${id}`, { method: 'DELETE' }),
  test: (id: string) =>
    request<ConnectionTestResult>(`/connections/${id}/test`, { method: 'POST' }),
  testNew: (data: ConnectionCreate) =>
    request<ConnectionTestResult>('/connections/test', { method: 'POST', body: JSON.stringify(data) }),
  discover: (id: string, config?: Partial<ScanConfig>) =>
    request<RuleCreate[]>(`/connections/${id}/discover`, {
      method: 'POST',
      body: JSON.stringify(config || {}),
    }),
};

// ---- Rules ----
export const rulesApi = {
  list: (params?: PaginationParams) =>
    request<PaginatedResponse<MaskingRule>>(`/rules/${queryParams(params || {})}`),
  listAll: () => request<MaskingRule[]>('/rules/'),
  get: (id: string) => request<MaskingRule>(`/rules/${id}`),
  create: (data: RuleCreate) =>
    request<MaskingRule>('/rules/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<RuleCreate>) =>
    request<MaskingRule>(`/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/rules/${id}`, { method: 'DELETE' }),
  bulkDelete: (ids: string[]) =>
    request<{ deleted: number }>('/rules/bulk-delete', {
      method: 'POST',
      body: JSON.stringify({ ids }),
    }),
  bulkCreate: (rules: RuleCreate[]) =>
    request<MaskingRule[]>('/rules/bulk-create', {
      method: 'POST',
      body: JSON.stringify({ rules }),
    }),
};

// ---- Jobs ----
export const jobsApi = {
  list: (params?: PaginationParams) =>
    request<PaginatedResponse<MaskingJob>>(`/jobs/${queryParams(params || {})}`),
  listAll: () => request<MaskingJob[]>('/jobs/'),
  get: (id: string) => request<MaskingJob>(`/jobs/${id}`),
  create: (data: JobCreate) =>
    request<MaskingJob>('/jobs/', { method: 'POST', body: JSON.stringify(data) }),
  run: (id: string) =>
    request<{ message: string }>(`/jobs/${id}/run`, { method: 'POST' }),
  cancel: (id: string) =>
    request<{ message: string }>(`/jobs/${id}/cancel`, { method: 'POST' }),
  unmask: (id: string) =>
    request<{ message: string }>(`/jobs/${id}/unmask`, { method: 'POST' }),
  delete: (id: string) =>
    request<void>(`/jobs/${id}`, { method: 'DELETE' }),
  query: (id: string, mask?: boolean) => {
    const q = mask !== undefined ? `?mask=${mask}` : '';
    return request<DynamicQueryResponse>(`/jobs/${id}/query${q}`);
  },
  share: (id: string, data: ShareJobRequest) =>
    request<{ message: string }>(`/jobs/${id}/share`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  unshare: (id: string, email: string) =>
    request<{ message: string }>(`/jobs/${id}/unshare`, {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),
  audit: (id: string) =>
    request<AuditLogEntry[]>(`/jobs/${id}/audit`),
  preview: (connectionId: string, ruleIds: string[]) =>
    request<DynamicQueryResponse>('/jobs/preview', {
      method: 'POST',
      body: JSON.stringify({ connection_id: connectionId, rule_ids: ruleIds }),
    }),
};

// ---- Discovery ----
export const discoveryApi = {
  startScan: (config: ScanConfig) =>
    request<DiscoveryScan>('/discovery/scan', {
      method: 'POST',
      body: JSON.stringify(config),
    }),
  getScan: (id: string) =>
    request<DiscoveryScan>(`/discovery/scan/${id}`),
  listScans: (connectionId?: string) =>
    request<DiscoveryScan[]>(`/discovery/scans${connectionId ? `?connection_id=${connectionId}` : ''}`),
  getResults: (scanId: string) =>
    request<DiscoveryResult[]>(`/discovery/scan/${scanId}/results`),
  createRulesFromResults: (resultIds: string[]) =>
    request<MaskingRule[]>('/discovery/create-rules', {
      method: 'POST',
      body: JSON.stringify({ result_ids: resultIds }),
    }),
};

// ---- Reports ----
export const reportsApi = {
  summary: () => request<Summary>('/reports/summary'),
  compliance: (framework?: string) =>
    request<ComplianceReport>(`/reports/compliance${framework ? `?framework=${framework}` : ''}`),
  riskAssessment: () =>
    request<{ overall_risk: number; items: import('../types').RiskItem[] }>('/reports/risk'),
  exportReport: (format: ExportFormat, type: string) =>
    request<Blob>(`/reports/export?format=${format}&type=${type}`, {
      headers: { Accept: 'application/octet-stream' },
    }),
};

// ---- Schedules ----
export const schedulesApi = {
  list: () => request<Schedule[]>('/schedules/'),
  get: (id: string) => request<Schedule>(`/schedules/${id}`),
  create: (data: ScheduleCreate) =>
    request<Schedule>('/schedules/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: Partial<ScheduleCreate>) =>
    request<Schedule>(`/schedules/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/schedules/${id}`, { method: 'DELETE' }),
  toggle: (id: string, enabled: boolean) =>
    request<Schedule>(`/schedules/${id}/toggle`, {
      method: 'POST',
      body: JSON.stringify({ enabled }),
    }),
  history: (id: string) =>
    request<ScheduleHistory[]>(`/schedules/${id}/history`),
};

// ---- Settings ----
export const settingsApi = {
  getProfile: () => request<User>('/settings/profile'),
  updateProfile: (data: Partial<User>) =>
    request<User>('/settings/profile', { method: 'PUT', body: JSON.stringify(data) }),
  getApiKeys: () => request<ApiKey[]>('/settings/api-keys'),
  createApiKey: (name: string, scopes: string[], expiresAt?: string) =>
    request<ApiKey & { key: string }>('/settings/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name, scopes, expires_at: expiresAt }),
    }),
  deleteApiKey: (id: string) =>
    request<void>(`/settings/api-keys/${id}`, { method: 'DELETE' }),
  getNotifications: () =>
    request<NotificationPreference>('/settings/notifications'),
  updateNotifications: (data: Partial<NotificationPreference>) =>
    request<NotificationPreference>('/settings/notifications', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

// ---- Plugins ----
export const pluginsApi = {
  list: () => request<Plugin[]>('/plugins/'),
  get: (id: string) => request<Plugin>(`/plugins/${id}`),
  toggle: (id: string, enabled: boolean) =>
    request<Plugin>(`/plugins/${id}/toggle`, {
      method: 'POST',
      body: JSON.stringify({ enabled }),
    }),
  configure: (id: string, config: Record<string, unknown>) =>
    request<Plugin>(`/plugins/${id}/configure`, {
      method: 'POST',
      body: JSON.stringify({ config }),
    }),
};

// ---- Admin ----
export const adminApi = {
  users: () => request<User[]>('/admin/users/'),
  updateUserRole: (id: string, role: string) =>
    request<User>(`/admin/users/${id}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    }),
  deleteUser: (id: string) =>
    request<void>(`/admin/users/${id}`, { method: 'DELETE' }),
  auditLog: (params?: PaginationParams) =>
    request<PaginatedResponse<AuditLogEntry>>(`/admin/audit${queryParams(params || {})}`),
  systemHealth: () =>
    request<{ status: string; version: string; uptime: number; db_connected: boolean }>(
      '/admin/health',
    ),
};
