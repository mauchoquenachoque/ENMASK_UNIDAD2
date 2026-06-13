export class EnmaskError extends Error {
  public statusCode?: number;
  public details: Record<string, unknown>;

  constructor(
    message: string,
    statusCode?: number,
    details: Record<string, unknown> = {}
  ) {
    super(message);
    this.name = "EnmaskError";
    this.statusCode = statusCode;
    this.details = details;
  }

  toString(): string {
    if (this.statusCode) {
      return `[${this.statusCode}] ${this.message}`;
    }
    return this.message;
  }
}

export class AuthenticationError extends EnmaskError {
  constructor(message = "Authentication failed") {
    super(message, 401);
    this.name = "AuthenticationError";
  }
}

export class AuthorizationError extends EnmaskError {
  constructor(message = "Insufficient permissions") {
    super(message, 403);
    this.name = "AuthorizationError";
  }
}

export class NotFoundError extends EnmaskError {
  constructor(resource = "Resource") {
    super(`${resource} not found`, 404);
    this.name = "NotFoundError";
  }
}

export class ValidationError extends EnmaskError {
  constructor(message = "Validation error") {
    super(message, 422);
    this.name = "ValidationError";
  }
}

export class RateLimitError extends EnmaskError {
  constructor(message = "Rate limit exceeded") {
    super(message, 429);
    this.name = "RateLimitError";
  }
}

export class ServerError extends EnmaskError {
  constructor(message = "Internal server error") {
    super(message, 500);
    this.name = "ServerError";
  }
}

export class ConnectionError extends EnmaskError {
  constructor(message = "Connection failed") {
    super(message);
    this.name = "ConnectionError";
  }
}
