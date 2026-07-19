const EventEmitter = require('events');
const crypto = require('crypto');

class TrafficController extends EventEmitter {
  constructor(options = {}) {
    super();
    this.nodeId = options.nodeId || 'default';
    this.maxBandwidthBps = options.maxBandwidthBps || 100000000;
    this.currentBandwidth = 0;
    this.windowMs = options.windowMs || 1000;
    this.windowStart = Date.now();
    this.bytesInWindow = 0;
    this.throttleThreshold = options.throttleThreshold || 0.8;
    this.throttled = false;
    this.priorityQueue = [];
    this.processing = false;
    this.buffer = options.bufferSize || 65536;
    this.droppedPackets = 0;
    this.totalProcessed = 0;
    this.qos = {
      minGuaranteed: options.minGuaranteed || 10,
      maxBurst: options.maxBurst || 1000,
      fairShare: true
    };
    this.metrics = {
      avgLatency: 0,
      latencySamples: [],
      maxLatency: 0,
      minLatency: Infinity,
      throughput: 0,
      packetLoss: 0
    };
    this.maxLatencySamples = options.maxLatencySamples || 1000;
    this.intrusionDetector = {
      suspiciousIPs: new Map(),
      threshold: options.intrusionThreshold || 100,
      windowMs: options.intrusionWindowMs || 60000,
      banned: new Set()
    };
  }

  enqueue(packet, priority = 5) {
    if (this.throttled && priority < 15) {
      this.droppedPackets++;
      this.emit('dropped', { reason: 'throttled', packetId: packet.id, priority });
      return false;
    }

      if (this.bytesInWindow >= this.maxBandwidthBps * this.windowMs / 1000) {
      this.droppedPackets++;
      this.emit('dropped', { reason: 'bandwidth_exceeded', packetId: packet.id });
      return false;
    }

    const entry = {
      packet,
      priority,
      enqueuedAt: Date.now(),
      id: packet.id
    };

    this.priorityQueue.push(entry);
    this.priorityQueue.sort((a, b) => b.priority - a.priority);

    if (!this.processing) this._processQueue();

    this.emit('enqueued', { packetId: packet.id, priority, queueLength: this.priorityQueue.length });
    return true;
  }

  _processQueue() {
    this.processing = true;

    const processNext = () => {
      if (this.priorityQueue.length === 0) {
        this.processing = false;
        return;
      }

      const now = Date.now();
      const windowElapsed = now - this.windowStart;

      if (windowElapsed >= this.windowMs) {
        this.currentBandwidth = this.bytesInWindow / (windowElapsed / 1000);
        this.bytesInWindow = 0;
        this.windowStart = now;

        if (this.currentBandwidth > this.maxBandwidthBps * this.throttleThreshold) {
          this.throttled = true;
          this.emit('throttle_start', { bandwidth: this.currentBandwidth });
        } else if (this.currentBandwidth < this.maxBandwidthBps * (this.throttleThreshold * 0.5)) {
          this.throttled = false;
          this.emit('throttle_end', { bandwidth: this.currentBandwidth });
        }
      }

      const entry = this.priorityQueue.shift();
      const latency = Date.now() - entry.enqueuedAt;

      this._updateLatencyMetrics(latency);
      this.bytesInWindow += this._estimatePacketSize(entry.packet);
      this.totalProcessed++;

      this.emit('processed', {
        packetId: entry.packet.id,
        priority: entry.priority,
        latency,
        queueSize: this.priorityQueue.length,
        nodeId: this.nodeId
      });

      setImmediate(processNext);
    };

    processNext();
  }

  _estimatePacketSize(packet) {
    return Buffer.byteLength(JSON.stringify(packet.toJSON ? packet.toJSON() : packet));
  }

  _updateLatencyMetrics(latency) {
    this.metrics.latencySamples.push(latency);
    if (this.metrics.latencySamples.length > this.maxLatencySamples) this.metrics.latencySamples.shift();

    this.metrics.avgLatency = this.metrics.latencySamples.reduce((a, b) => a + b, 0) / this.metrics.latencySamples.length;
    this.metrics.maxLatency = Math.max(this.metrics.maxLatency, latency);
    this.metrics.minLatency = Math.min(this.metrics.minLatency, latency);
    this.metrics.throughput = this.totalProcessed / ((Date.now() - this.windowStart) / 1000 || 1);
  }

  inspectTraffic(fromIP) {
    const key = fromIP;
    const now = Date.now();
    const record = this.intrusionDetector.suspiciousIPs.get(key) || { count: 0, firstSeen: now, lastSeen: now };
    record.count++;
    record.lastSeen = now;
    this.intrusionDetector.suspiciousIPs.set(key, record);

    if (record.count > this.intrusionDetector.threshold) {
      this.intrusionDetector.banned.add(fromIP);
      this.emit('intrusion_detected', { ip: fromIP, count: record.count, action: 'banned' });
      return { suspicious: true, banned: true, count: record.count };
    }

    return { suspicious: record.count > this.intrusionDetector.threshold * 0.5, count: record.count };
  }

  getMetrics() {
    return {
      nodeId: this.nodeId,
      throttled: this.throttled,
      currentBandwidth: this.currentBandwidth,
      maxBandwidth: this.maxBandwidthBps,
      queueDepth: this.priorityQueue.length,
      droppedPackets: this.droppedPackets,
      totalProcessed: this.totalProcessed,
      bandwidth: this.currentBandwidth,
      latency: this.metrics,
      qos: this.qos,
      intrusion: {
        suspiciousIPs: this.intrusionDetector.suspiciousIPs.size,
        banned: this.intrusionDetector.banned.size
      },
      utilization: (this.currentBandwidth / this.maxBandwidthBps * 100).toFixed(2)
    };
  }

  destroy() {
    this.priorityQueue.length = 0;
    this.intrusionDetector.suspiciousIPs.clear();
    this.intrusionDetector.banned.clear();
    this.removeAllListeners();
  }
}

module.exports = { TrafficController };
