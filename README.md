# 项目数据库迁移教程

## 注意

- 在新创建数据表之后要将model添加到`persist/model/__init__.py`中
- 随后执行`python -m alembic --autogenerate`命令生成迁移文件
- 提交之后再项目启动时会自动执行迁移文件, 逻辑文件在`.docker/docker-entrypoint.sh`中


## 数据库迁移工具alembic

- 增删改model之后执行
```bash
python -m alembic revision --autogenerate
```

- 生成迁移文件后，执行
```bash
python -m alembic upgrade head
```
- 回滚到上一个版本
```bash
python -m alembic downgrade -1
```

- 回滚到指定版本
```bash
python -m alembic downgrade <version>
```

- 查看当前版本
```bash
python -m alembic current
```

- 查看版本历史
```bash
python -m alembic history
```

- 查看版本差异
```bash
python -m alembic history --verbose
```

- fake(伪造迁移) 当数据库存在时，没有迁移文件，映射model时执行
```bash
python -m alembic stamp head
```