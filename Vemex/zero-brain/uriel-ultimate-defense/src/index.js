const { runRenderParadoxSimulation } = require('./simulate');

if (require.main === module) {
  runRenderParadoxSimulation();
}

module.exports = { runRenderParadoxSimulation };
