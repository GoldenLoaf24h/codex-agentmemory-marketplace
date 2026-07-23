import { ISdk } from "iii-sdk";

//#region src/state/kv.d.ts
declare class StateKV {
  private sdk;
  constructor(sdk: ISdk);
  get<T = unknown>(scope: string, key: string): Promise<T | null>;
  set<T = unknown>(scope: string, key: string, data: T): Promise<T>;
  delete(scope: string, key: string): Promise<void>;
  list<T = unknown>(scope: string): Promise<T[]>;
}
//#endregion
//#region src/functions/diagnostics.d.ts
declare function registerDiagnosticsFunction(sdk: ISdk, kv: StateKV): void;
//#endregion
export { registerDiagnosticsFunction };
//# sourceMappingURL=diagnostics.d.mts.map