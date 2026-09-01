import "@testing-library/jest-dom/vitest";

if (typeof window.localStorage.clear !== "function") {
  const values = new Map<string, string>();
  const localStorageMock: Storage = {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key) => values.get(String(key)) ?? null,
    key: (index) => Array.from(values.keys())[index] ?? null,
    removeItem: (key) => values.delete(String(key)),
    setItem: (key, value) => values.set(String(key), String(value)),
  };
  Object.defineProperty(window, "localStorage", {
    configurable: true,
    value: localStorageMock,
  });
}

Object.defineProperty(window, "scrollTo", { value: () => undefined, writable: true });
