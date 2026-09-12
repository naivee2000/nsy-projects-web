import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteStaticCopy } from "vite-plugin-static-copy";
export default defineConfig({
    plugins: [
        react(),
        viteStaticCopy({
            targets: [{
                    src: "node_modules/pyodide/{pyodide.js,pyodide.asm.js,pyodide.asm.wasm,pyodide-lock.json,python_stdlib.zip}",
                    dest: "pyodide",
                    rename: { stripBase: true },
                }, {
                    src: "node_modules/monaco-editor/min/vs",
                    dest: "monaco",
                    rename: { stripBase: 3 },
                }],
        }),
    ],
    server: {
        host: "127.0.0.1",
        port: 5173,
        proxy: { "/api": "http://127.0.0.1:8765" },
    },
});
