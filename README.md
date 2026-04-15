# Google Design Fusion Workspace

这个目录现在承载 3 层产物：

## 1. `google-design-vector-db/`

本地设计向量库。

内容来源：

- `design.google` sitemap 深度抓取结果
- 选择性纳入的高价值外部设计参考
- `awesome-design-md` 的 `DESIGN.md / README.md`

当前构建结果：

- `design.google` crawl 记录：`328`
- `design.google` 原站可索引页面：`248`
- `design.google` 外部高价值参考：`32`
- `awesome-design-md` 样本：`54`
- 检索 chunk：`6457`

关键文件：

- `manifest.json`
- `crawl-summary.json`
- `crawl-report.jsonl`
- `index.json`
- `records.jsonl`
- `chunks.jsonl`
- `site-map.json`
- `README.md`

## 2. `research/`

人工整理后的中文研究文档：

- `design-google-site-map.md`
- `design-google-principles.md`
- `google-design-awesome-fusion.md`
- `ai-design-antipatterns.md`
- `validation-report.md`

## 3. `skills/google-design-fusion/`

最终 skill 本体。

包含：

- `SKILL.md`
- `agents/openai.yaml`
- `references/*.md`
- `scripts/*.py`

关键脚本：

- `scripts/build_design_fusion_vector_db.py`
- `scripts/design_harness.py`
- `scripts/validate_harness.py`
- `scripts/validate_skill_contract.py`
- `scripts/validate_workspace_docs.py`
- `scripts/run_full_validation.py`

## 常用命令

重建向量库：

```bash
python skills/google-design-fusion/scripts/build_design_fusion_vector_db.py
```

查询检索 harness：

```bash
python skills/google-design-fusion/scripts/design_harness.py "brand-forward premium landing page typography" --phase ui --top-k 8
```

跑整套验证：

```bash
python skills/google-design-fusion/scripts/run_full_validation.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and validation expectations.

## License

MIT License - see [LICENSE](LICENSE)
