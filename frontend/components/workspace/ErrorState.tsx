import { AlertCircle } from "lucide-react";

type ErrorStateProps = {
  onRetry: () => void;
};

export function ErrorState({ onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-workspace-danger/40 bg-workspace-danger/10 p-8 text-center">
      <AlertCircle className="mx-auto h-9 w-9 text-workspace-danger" />
      <h3 className="mt-3 text-lg font-bold text-workspace-text">模拟错误状态</h3>
      <p className="mt-2 text-sm text-workspace-muted">这里用于验证模块失败时的页面反馈，不代表真实接口异常。</p>
      <button className="mt-5 h-10 rounded-md bg-workspace-primary px-4 text-sm font-bold text-white" type="button" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}
