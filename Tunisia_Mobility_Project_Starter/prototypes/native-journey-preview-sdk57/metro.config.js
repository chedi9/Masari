const path = require('path');
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);
const appSource = path.resolve(__dirname, '../../apps/mobile');

config.watchFolders = [path.join(appSource, 'app'), path.join(appSource, 'src')];
config.resolver.disableHierarchicalLookup = true;
config.resolver.nodeModulesPaths = [path.resolve(__dirname, 'node_modules')];

module.exports = config;
