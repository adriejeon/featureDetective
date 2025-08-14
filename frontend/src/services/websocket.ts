import io from "socket.io-client";

export interface JobProgress {
  progress: number;
  current_step: string;
  status: string;
}

export interface JobCompleted {
  success: boolean;
  data: any;
  message: string;
}

export interface JobFailed {
  success: boolean;
  error: string;
  message: string;
}

class WebSocketService {
  private socket: any = null;
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket && this.isConnected) {
        resolve();
        return;
      }

      this.socket = io("http://127.0.0.1:5004", {
        transports: ["websocket", "polling"],
        timeout: 20000,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: 1000,
      });

      this.socket.on("connect", () => {
        console.log("웹소켓 연결됨");
        this.isConnected = true;
        this.reconnectAttempts = 0;
        resolve();
      });

      this.socket.on("disconnect", () => {
        console.log("웹소켓 연결 해제");
        this.isConnected = false;
      });

      this.socket.on("connect_error", (error: any) => {
        console.error("웹소켓 연결 오류:", error);
        this.reconnectAttempts++;
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          reject(new Error("웹소켓 연결 실패"));
        }
      });

      this.socket.on("error", (error: any) => {
        console.error("웹소켓 오류:", error);
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  joinJob(jobId: string): void {
    console.log("=== joinJob 호출 ===");
    console.log("socket 존재:", !!this.socket);
    console.log("연결 상태:", this.isConnected);
    console.log("Job ID:", jobId);

    if (this.socket && this.isConnected) {
      console.log("Job 구독 이벤트 전송:", { job_id: jobId });
      this.socket.emit("join_job", { job_id: jobId });
    } else {
      console.error("웹소켓이 연결되지 않아 Job 구독할 수 없음");
    }
  }

  leaveJob(jobId: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit("leave_job", { job_id: jobId });
    }
  }

  onJobProgress(callback: (data: JobProgress) => void): void {
    if (this.socket) {
      this.socket.on("job_progress", callback);
    }
  }

  onJobCompleted(callback: (data: JobCompleted) => void): void {
    if (this.socket) {
      this.socket.on("job_completed", callback);
    }
  }

  onJobFailed(callback: (data: JobFailed) => void): void {
    if (this.socket) {
      this.socket.on("job_failed", callback);
    }
  }

  onConnected(callback: (data: any) => void): void {
    if (this.socket) {
      this.socket.on("connected", callback);
    }
  }

  onJoinedJob(callback: (data: any) => void): void {
    if (this.socket) {
      this.socket.on("joined_job", callback);
    }
  }

  onLeftJob(callback: (data: any) => void): void {
    if (this.socket) {
      this.socket.on("left_job", callback);
    }
  }

  removeAllListeners(): void {
    if (this.socket) {
      this.socket.removeAllListeners();
    }
  }

  isSocketConnected(): boolean {
    return this.isConnected;
  }
}

export const websocketService = new WebSocketService();
export default websocketService;
