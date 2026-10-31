import { cpSync, mkdirSync } from 'node:fs';
mkdirSync('public/cesium', { recursive: true });
for (const folder of ['Assets', 'ThirdParty', 'Widgets', 'Workers']) cpSync(`node_modules/cesium/Build/Cesium/${folder}`, `public/cesium/${folder}`, { recursive: true });
