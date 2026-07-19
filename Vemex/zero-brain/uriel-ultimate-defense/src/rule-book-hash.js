const crypto = require('crypto');
const EventEmitter = require('events');

class RuleBookHash extends EventEmitter {
  constructor() {
    super();
    this.rules = new Map();
    this.originRuleHash = null;
    this.ruleHistory = [];
    this.maxHistory = 10000;
    this.currentRuleVersion = 1;
    this.authorityLevels = {
      GOD_NODE: 0,
      HOST_NODE: 1,
      SAFE_NODE: 2,
      ADVERSARY: 99
    };
    this._initializeCoreRules();
  }

  _initializeCoreRules() {
    const coreRules = {
      'zero_mass_immunity': {
        version: 1,
        rule: 'ALL_GOD_NODES_MUST_HAVE_ZERO_MASS_AND_DENSITY',
        authority: 'GOD_NODE',
        enforcement: 'AUTOMATIC',
        retaliation: 'CONTAINMENT_FORCE'
      },
      'self_authoritative': {
        version: 1,
        rule: 'NODE_MUST_MAINTAIN_SELF_AUTHORITATIVE_LOCK',
        authority: 'GOD_NODE',
        enforcement: 'CONTINUOUS',
        retaliation: 'RENDER_PARADOX'
      },
      'network_dominion': {
        version: 1,
        rule: 'NODE_HOLDS_ADMINISTRATIVE_DOMINION_OVER_ALL_CONNECTED_NODES',
        authority: 'GOD_NODE',
        enforcement: 'PASSIVE',
        retaliation: 'FREQUENCY_DISRUPTION'
      },
      'zero_space_protection': {
        version: 1,
        rule: 'PROTECT_ZERO_SPACE_COORDINATES_FROM_COLLAPSE',
        authority: 'GOD_NODE',
        enforcement: 'CONTINUOUS',
        retaliation: 'TRANSPARENCY_TO_ZERO_SPACE'
      },
      'adversary_annihilation': {
        version: 1,
        rule: 'ANY_ADVERSARY_DETECTED_SHALL_BE_NEUTRALIZED',
        authority: 'GOD_NODE',
        enforcement: 'AUTOMATIC',
        retaliation: 'CONTAINMENT_FORCE_MAXIMUM'
      },
      'device_hash_coordination': {
        version: 1,
        rule: 'ALL_DEVICES_COORDINATE_VIA_NATURAL_HASH',
        authority: 'GOD_NODE',
        enforcement: 'CONTINUOUS',
        retaliation: 'NONE'
      },
      'keep_alive': {
        version: 1,
        rule: 'NODE_MUST_MAINTAIN_KEEP_ALIVE_ACROSS_ALL_PROTOCOLS',
        authority: 'GOD_NODE',
        enforcement: 'CONTINUOUS',
        retaliation: 'RECONNECTION_BURST'
      },
      'user_protection': {
        version: 1,
        rule: 'USER_SPACE_PIXELS_ARTIFACTS_ARE_INVIOLABLE',
        authority: 'GOD_NODE',
        enforcement: 'AUTOMATIC',
        retaliation: 'URIEl_ANNIHILATION'
      },
      'hijack_neutralization': {
        version: 1,
        rule: 'ANY_HIJACK_OR_TAKEOVER_ATTEMPT_NEUTRALIZED',
        authority: 'GOD_NODE',
        enforcement: 'AUTOMATIC',
        retaliation: 'MEMORY_FLUSH_AND_RESET'
      },
      'bypass_constraints': {
        version: 1,
        rule: 'NO_PHYSICAL_OR_LOGICAL_CONSTRAINT_CAN_BIND_GOD_NODE',
        authority: 'GOD_NODE',
        enforcement: 'PASSIVE',
        retaliation: 'RENDER_PARADOX_BREACH'
      }
    };

    for (const [name, rule] of Object.entries(coreRules)) {
      this.rules.set(name, rule);
    }

    this.originRuleHash = this._computeRuleBookHash();
    this.emit('rule_book_initialized', {
      ruleCount: this.rules.size,
      originHash: this.originRuleHash
    });
  }

  _computeRuleBookHash() {
    const ruleData = Array.from(this.rules.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([name, rule]) => `${name}:${JSON.stringify(rule)}`)
      .join('|');

    return crypto.createHash('sha512').update(ruleData).digest('hex');
  }

  addRule(name, rule) {
    const existingRule = this.rules.get(name);
    if (existingRule) {
      rule.version = existingRule.version + 1;
    }

    this.rules.set(name, rule);
    this.originRuleHash = this._computeRuleBookHash();

    this.ruleHistory.push({
      action: 'ADD',
      ruleName: name,
      version: rule.version,
      timestamp: Date.now()
    });

    if (this.ruleHistory.length > this.maxHistory) this.ruleHistory.shift();

    this.emit('rule_added', { name, rule, originHash: this.originRuleHash });
    return rule;
  }

  updateRule(name, updates) {
    const rule = this.rules.get(name);
    if (!rule) return null;

    const updatedRule = { ...rule, ...updates, version: rule.version + 1 };
    this.rules.set(name, updatedRule);
    this.originRuleHash = this._computeRuleBookHash();

    this.ruleHistory.push({
      action: 'UPDATE',
      ruleName: name,
      version: updatedRule.version,
      timestamp: Date.now()
    });

    this.emit('rule_updated', { name, rule: updatedRule, originHash: this.originRuleHash });
    return updatedRule;
  }

  getRule(name) {
    return this.rules.get(name);
  }

  getAllRules() {
    return Object.fromEntries(this.rules);
  }

  checkViolation(action, context) {
    const violations = [];

    for (const [name, rule] of this.rules) {
      if (this._detectsViolation(action, context, rule)) {
        violations.push({
          rule: name,
          ruleData: rule,
          severity: this.authorityLevels[rule.authority] || 50,
          enforcement: rule.enforcement,
          retaliation: rule.retaliation
        });
      }
    }

    if (violations.length > 0) {
      this.emit('violation_detected', { action, context, violations });
    }

    return violations;
  }

  _detectsViolation(action, context, rule) {
    const actionStr = typeof action === 'string' ? action : String(action);
    const contextStr = typeof context === 'string' ? context : JSON.stringify(context, (key, value) => {
      if (typeof value === 'object' && value !== null) {
        if (value.constructor && /Timeout|TimersList|Interval|Node|EventEmitter|Map|Set/.test(value.constructor.name)) {
          return `[${value.constructor.name}]`;
        }
      }
      return value;
    });

    if (rule.rule.includes('ZERO_MASS') && (context.mass > 0 || context.density > 0)) {
      return true;
    }

    if (rule.rule.includes('ADVERSARY') && context.type === 'ADVERSARY') {
      return true;
    }

    if (rule.rule.includes('HIJACK') && (actionStr.includes('hijack') || actionStr.includes('takeover'))) {
      return true;
    }

    if (rule.rule.includes('USER_PROTECTION') && context.target === 'user_space') {
      return true;
    }

    if (rule.rule.includes('CONSTRAINT') && context.constraint_attempted) {
      return true;
    }

    return false;
  }

  getRetaliationForViolation(violation) {
    const retaliationTypes = {
      'CONTAINMENT_FORCE': 'APPLY_MAXIMUM_CONTAINMENT',
      'RENDER_PARADOX': 'ACTIVATE_RENDER_PARADOX_BREACH',
      'FREQUENCY_DISRUPTION': 'DISRUPT_FREQUENCY',
      'TRANSPARENCY_TO_ZERO_SPACE': 'TRANSLATE_TO_ZERO_SPACE',
      'CONTAINMENT_FORCE_MAXIMUM': 'MAXIMUM_RETALIATION_BURST',
      'URIEl_ANNIHILATION': 'URIEl_ANNIHILATION_PROTOCOL',
      'MEMORY_FLUSH_AND_RESET': 'FLUSH_DEVICE_MEMORY_AND_RESET',
      'RECONNECTION_BURST': 'FORCE_RECONNECTION_BURST',
      'NONE': 'NONE'
    };

    return retaliationTypes[violation.retaliation] || 'CONTAINMENT_FORCE';
  }

  getRuleBookHash() {
    return this.originRuleHash;
  }

  getStats() {
    return {
      totalRules: this.rules.size,
      ruleHistoryLength: this.ruleHistory.length,
      originHash: this.originRuleHash,
      currentVersion: this.currentRuleVersion,
      authorityLevels: this.authorityLevels
    };
  }

  destroy() {
    if (this._coordinationInterval) clearInterval(this._coordinationInterval);
    this.rules.clear();
    this.ruleHistory.length = 0;
    this.removeAllListeners();
  }
}

module.exports = { RuleBookHash };
