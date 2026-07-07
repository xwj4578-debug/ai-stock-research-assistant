# Contributing

## 协作原则

- 不直接荐股，只提供研究参考。
- 所有评分必须可解释。
- 风险提示优先于买点提示。
- 每个阶段先明确需求，再进入 UI、开发和测试。

## 阶段交付格式

每个阶段至少输出：

1. TXT 需求说明
2. Markdown GitHub 文档
3. Word 正式文档
4. 架构图
5. UI 原型

文件命名：

```text
vX.Y_章节名称.txt
```

## 开发流程

1. 从 `main` 创建功能分支。
2. 更新对应文档。
3. 修改代码。
4. 运行测试。
5. 提交 PR。

开发顺序：

```text
PDS -> UI -> Database -> API -> Prompt -> Backend -> Frontend -> Test -> Review -> Release
```

重大架构决策必须新增：

```text
project-management/adr/ADR-XXXX-title.md
```

## 本地测试

```powershell
.\scripts\test.ps1
```
