### G2和G2Plot对比

1. G2 作为底层依赖，使用了图形语法，上手成本相对较高，功能强大
2. G2Plot 全面依赖 G2，G2Plot 层仅仅是基于 G2 强大的图形、交互、事件、动画能力，一图一做的扩展不同的常见业务图表，开箱即用、易于配置

### 目标

- [ ] 解析[G2Plot基础案例](https://g2plot.antv.vision/zh/docs/api/plots/line)生成一组**chart jsonschema**
- [ ] 基于[G2Plot源码中的examples](https://github.com/antvis/G2Plot/tree/master/examples)向配置填入默认值
- [ ] 可视化平台，表单配置jsonschema，动态配置报表
- [ ] 被redash继承，查询结果能填入G2Plot

### 代码结构

```shell
.
├── antv_jsonschema
│   ├── core
│   ├── resources
│   │   ├── G2Plot                  # g2plot源码
│   │   └── g2plot.antv.vision      # wget镜像官方文档，提取信息用于结构化scchema
│   ├── scripts                     # 脚本
│   ├── tests
│   │   └── unit                    # 单元测测试
│   └── utils                       # 工具类
├── etc                             # 项目配置
├── run                             # 运行时产生，如pid
└── var                             # 静态文件或日志等
```

### 常用命令

```shell
# 克隆文档
wget -r -p -np -k -E https://g2plot.antv.vision/zh/docs/api/plots/line
```