# Backend

后端当前使用 FastAPI。

启动：

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8010
```

测试：

```powershell
python -m pytest backend/tests
```
