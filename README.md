`auto_http_load` 基于Apache Benchmark做压力测试，并将压测结果使用matplotlib绘制成图。

### 依赖

- Apache Benchmark
- Python第三方库：matplotlib


### 使用

1. 根据需求修改配置文件`config.json`
2. 执行python http_load.py，http_load.py支持两个命令选项，执行`python http_load.py -h`可查看帮助文档
    - `-c`：用于指定配置文件的路径，默认为当前路径下的`config.json`文件
    - `-v`：用于指定是否需要额外的数据输出：将每次的压测结果写到json文件中，并在标准输出打印压测结果