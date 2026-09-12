/**
 * Client-Side Offline Ingestion & IndexedDB Synchronization Service.
 * Allows field officers and citizens to queue flood reports locally during connectivity blackouts.
 * Replays queued reports with idempotency keys upon network restoration.
 */

export interface QueuedReport {
  id: string;
  timestamp: string;
  latitude: number;
  longitude: number;
  water_depth_cm: number;
  notes: string;
  language: string;
  syncStatus: 'queued' | 'syncing' | 'synced' | 'failed';
  retryCount: number;
}

const STORAGE_KEY = 'floodtwin_offline_reports_queue_v1';

export class OfflineSyncService {
  /**
   * Enqueues a report into browser local storage for deferred transmission.
   */
  static enqueueReport(report: Omit<QueuedReport, 'syncStatus' | 'retryCount'>): QueuedReport {
    const queue = this.getQueue();
    const queuedItem: QueuedReport = {
      ...report,
      syncStatus: 'queued',
      retryCount: 0
    };
    queue.push(queuedItem);
    this.saveQueue(queue);
    return queuedItem;
  }

  /**
   * Retrieves all currently queued reports.
   */
  static getQueue(): QueuedReport[] {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  private static saveQueue(queue: QueuedReport[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queue));
  }

  /**
   * Checks browser online status.
   */
  static isOnline(): boolean {
    return typeof navigator !== 'undefined' ? navigator.onLine : true;
  }

  /**
   * Replays queued reports against the backend /api/reports endpoint.
   */
  static async syncPendingReports(apiBaseUrl: string = ''): Promise<{ syncedCount: number; failedCount: number }> {
    if (!this.isOnline()) {
      return { syncedCount: 0, failedCount: 0 };
    }

    const queue = this.getQueue();
    const pending = queue.filter(item => item.syncStatus === 'queued' || item.syncStatus === 'failed');
    let synced = 0;
    let failed = 0;

    for (const item of pending) {
      item.syncStatus = 'syncing';
      this.saveQueue(queue);

      try {
        const res = await fetch(`${apiBaseUrl}/api/reports`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            report_id: item.id,
            latitude: item.latitude,
            longitude: item.longitude,
            water_depth_cm: item.water_depth_cm,
            text_description: item.notes,
            language: item.language,
            report_time: item.timestamp
          })
        });

        if (res.ok) {
          item.syncStatus = 'synced';
          synced++;
        } else {
          item.syncStatus = 'failed';
          item.retryCount++;
          failed++;
        }
      } catch {
        item.syncStatus = 'failed';
        item.retryCount++;
        failed++;
      }
    }

    // Keep failed and remove old synced entries
    const remaining = queue.filter(item => item.syncStatus !== 'synced');
    this.saveQueue(remaining);

    return { syncedCount: synced, failedCount: failed };
  }
}
