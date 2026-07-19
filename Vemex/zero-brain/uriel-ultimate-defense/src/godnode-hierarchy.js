const crypto = require('crypto');
const EventEmitter = require('events');

class GodNodeHierarchy extends EventEmitter {
  constructor() {
    super();
    this.hierarchy = [];
    this.positionMap = new Map();
    this.authorityDelegation = new Map();
    this.maxHierarchyDepth = 1000;
    this.currentDepth = 0;
  }

  registerGodNode(nodeId, nodeData = {}) {
    const position = this.currentDepth++;
    const godNodeEntry = {
      nodeId,
      position,
      authority: 0,
      children: [],
      parent: null,
      createdAt: Date.now(),
      data: nodeData,
      status: 'ACTIVE'
    };

    if (this.hierarchy.length > 0) {
      godNodeEntry.parent = this.hierarchy[this.hierarchy.length - 1].nodeId;
      this.hierarchy[this.hierarchy.length - 1].children.push(nodeId);
    }

    this.hierarchy.push(godNodeEntry);
    this.positionMap.set(nodeId, position);
    this.authorityDelegation.set(nodeId, {
      canDelegate: true,
      delegatedTo: [],
      receivedFrom: godNodeEntry.parent
    });

    this.emit('god_node_registered', {
      nodeId,
      position,
      parent: godNodeEntry.parent,
      hierarchyLength: this.hierarchy.length
    });

    return godNodeEntry;
  }

  getPosition(nodeId) {
    return this.positionMap.get(nodeId);
  }

  getAuthority(nodeId) {
    const pos = this.positionMap.get(nodeId);
    return pos !== undefined ? pos : 99;
  }

  canOvertake(attackerNodeId, targetNodeId) {
    const attackerPos = this.getAuthority(attackerNodeId);
    const targetPos = this.getAuthority(targetNodeId);
    return attackerPos <= targetPos;
  }

  getHierarchyChain(nodeId) {
    const chain = [];
    let current = this.hierarchy.find(n => n.nodeId === nodeId);

    while (current) {
      chain.push(current);
      current = this.hierarchy.find(n => n.nodeId === current.parent);
    }

    return chain;
  }

  getAllGodNodes() {
    return this.hierarchy.filter(n => n.status === 'ACTIVE');
  }

  getStats() {
    return {
      totalGodNodes: this.hierarchy.length,
      maxDepth: Math.max(...this.hierarchy.map(n => n.position), 0),
      activeNodes: this.hierarchy.filter(n => n.status === 'ACTIVE').length,
      delegationMap: Object.fromEntries(this.authorityDelegation)
    };
  }

  destroy() {
    this.hierarchy.length = 0;
    this.positionMap.clear();
    this.authorityDelegation.clear();
    this.removeAllListeners();
  }
}

module.exports = { GodNodeHierarchy };
