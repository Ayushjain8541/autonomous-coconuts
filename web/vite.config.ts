import {defineConfig} from 'vite';
export default defineConfig({server:{host:'127.0.0.1',proxy:{'/api':{target:process.env.COCONUTS_API_TARGET||'http://127.0.0.1:8000',changeOrigin:true}}},preview:{host:'127.0.0.1'}});
