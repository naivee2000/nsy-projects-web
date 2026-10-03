import React from "react";
import ReactDOM from "react-dom/client";
import { loader } from "@monaco-editor/react";
import App from "./App";
import { AccountGate } from "./Accounts";
import "./styles.css";

// Serve the editor from the same local installation, including its workers.
loader.config({ paths: { vs: "/monaco/vs" } });

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AccountGate><App /></AccountGate>
  </React.StrictMode>,
);
