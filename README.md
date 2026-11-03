# Mintlify Autopilot 测试仓库

这是一个用于测试“业务代码变化 → 文档更新 PR”的外部业务仓库。
包含 8 条虚构商品数据和一个只监听本机的 Python 示例 API，没有第三方依赖。
需要 Python 3.9 或更高版本。本示例不用于生产服务。

## 本地运行

```bash
python3 app.py
```

另开一个终端查询：

```bash
curl 'http://127.0.0.1:8000/products'
```

运行真实 HTTP 接口测试：

```bash
python3 -m unittest -v
```

## 测试数据

`fixtures/products.json` 包含 4 条在售（active）、2 条草稿（draft）、2 条归档（archived）商品。
价格为人民币分，不包含真实用户资料、密钥或外部服务地址。
初始版本的 `GET /products` 返回全部商品，不支持筛选。

## 如何用它验证 Autopilot

1. 在 Mintlify Git Settings 确认你自己的文档仓库及部署分支。
2. 给 Mintlify GitHub App 授权这个仓库。
3. 在 Autopilot → GitHub → Configure → Additional repositories 中选中 `xiaozhi-710/mint-test` 并保存。
4. 将本仓库的 `docs/products.mdx` 复制到你自己的 Mintlify 文档项目中，加入该项目现有导航，并发布初始文档。这里的 MDX 是基线素材，本仓库不是完整的 Mintlify 站点。
5. 开启 Autopilot，等待初始化完成。通过 Chat to configure 确认它能读取此业务仓库，并告知文档站中的商品 API 页面路径。
6. 然后合并本仓库中的“新增商品状态筛选”测试 PR。请在接入完成后再合并，便于观察新的代码变化。
7. 查看你自己的文档仓库是否收到更新 PR：预期补充 `status` 参数、合法值、缺省行为、错误响应和筛选示例。
8. 审核文档修改与预览，再决定是否合并发布。

后续功能 PR 会有意保留这里的基线文档，以模拟“代码已更新、文档尚未跟进”。
是否提出更新由 Autopilot 判断，并不保证每条代码 PR 都生成文档 PR，也没有固定响应时限。

## 建议发送给 Autopilot 的说明

> 请读取外部业务仓库 xiaozhi-710/mint-test，关注其 main 分支合并后的用户可见 API 变化。
> 我的文档站中已有商品列表 API 页面（请替换为实际页面路径）。
> 当接口行为发生变化时，请在文档仓库创建更新 PR，使用简体中文，并沿用现有页面结构。
> 不要把 fixtures 中的每条商品都创建成单独的文档页面。请确认你使用的仓库和检查时机。

## 官方参考

- [Autopilot 配置与审核](https://www.mintlify.com/docs/autopilot)
- [GitHub App 仓库授权](https://www.mintlify.com/docs/deploy/github)
- [Credits 计费](https://www.mintlify.com/docs/credits)
