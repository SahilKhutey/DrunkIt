/**
 * WebSocket client for real-time updates.
 */

export type RealtimeEvent = {
  type: string;
  channel: string;
  data: any;
  occurred_at: string;
};

export type EventHandler = (event: RealtimeEvent) => void;

export class RealtimeClient {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private channel: string;
  private handlers: Set<EventHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private heartbeatTimer: any = null;
  private closedByUser = false;

  constructor(options: { baseUrl: string; token: string; channel: string }) {
    this.token = options.token;
    this.channel = options.channel;
    const wsBase = options.baseUrl.replace(/^http/, 'ws');
    this.url = `${wsBase}/ws/${options.channel}?token=${encodeURIComponent(options.token)}`;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.closedByUser = false;
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        resolve();
      };

      this.ws.onerror = (e) => reject(e);

      this.ws.onmessage = (e) => {
        try {
          const event = JSON.parse(e.data);
          this.handlers.forEach((h) => h(event));
        } catch (err) {
          console.error('Failed to parse WS message', err);
        }
      };

      this.ws.onclose = () => {
        this.stopHeartbeat();
        if (!this.closedByUser && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => this.connect().catch(() => {}), Math.min(1000 * 2 ** this.reconnectAttempts, 30000));
        }
      };
    });
  }

  on(handler: EventHandler): () => void {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 25000);
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) clearInterval(this.heartbeatTimer);
    this.heartbeatTimer = null;
  }

  disconnect() {
    this.closedByUser = true;
    this.stopHeartbeat();
    this.ws?.close();
    this.ws = null;
  }
}
