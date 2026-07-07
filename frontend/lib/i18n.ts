import zhCN from "@/locales/zh-CN.json";

const messages: Record<string, string> = zhCN;

export function t(key: string) {
  return messages[key] ?? key;
}
