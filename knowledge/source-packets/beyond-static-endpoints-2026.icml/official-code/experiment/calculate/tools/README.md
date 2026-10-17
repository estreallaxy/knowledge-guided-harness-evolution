# 性能分析工具

这个工具用于分析DynamicWasm和MCP的测试结果，自动生成对比图表并计算性能差值。

## 功能特性

- 📊 自动读取测试结果JSON文件
- 📈 生成三个应用（MinIO、Directus、Memos）的性能对比条形图
- 📋 计算并打印详细的性能差值分析
- 📝 生成性能对比摘要报告
- 🎨 支持中文图表显示

## 分析的指标

- **平均执行时间** (duration_mean) - 越短越好
- **平均吞吐量** (throughput_mean) - 越高越好
- **平均网络流量** (total_bytes_mean) - 越少越好
- **成功率** (success_rate) - 越高越好
- **平均代码长度** (source_code_length_mean) - 越少越好

## 使用方法

### 方法1: 使用快速运行脚本（推荐）

```bash
cd experiment/calculate/tools
python run_analysis.py
```

这个脚本会自动使用 `results/9_21_dw/` 和 `results/9_21_mcp/` 目录中的测试结果。

### 方法2: 使用命令行工具

```bash
cd experiment/calculate/tools
python performance_analyzer.py <dw_path> <mcp_path> [选项]
```

#### 参数说明

- `dw_path`: DynamicWasm测试结果目录路径
- `mcp_path`: MCP测试结果目录路径

#### 选项

- `--output, -o`: 图表输出目录（默认: charts）
- `--report, -r`: 摘要报告文件名（默认: performance_summary.txt）

#### 使用示例

```bash
# 使用默认输出目录
python performance_analyzer.py ../results/9_21_dw ../results/9_21_mcp

# 指定输出目录和报告文件名
python performance_analyzer.py ../results/9_21_dw ../results/9_21_mcp -o my_charts -r my_report.txt
```

## 输出文件

运行分析后，会生成以下文件：

### 图表文件
- `duration_mean_comparison.png` - 平均执行时间对比图
- `throughput_mean_comparison.png` - 平均吞吐量对比图
- `total_bytes_mean_comparison.png` - 平均网络流量对比图
- `success_rate_comparison.png` - 成功率对比图
- `source_code_length_mean_comparison.png` - 平均代码长度对比图

### 报告文件
- `performance_summary.txt` - 性能对比摘要报告

## 目录结构要求

测试结果目录应包含以下JSON文件：

```
results/
├── 9_21_dw/
│   ├── MinIO_20250921_230751.json
│   ├── Directus_20250921_230650.json
│   └── Memos_20250921_230534.json
└── 9_21_mcp/
    ├── MinIO_20250921_223357.json
    ├── Directus_20250921_224132.json
    └── Memos_20250921_223245.json
```

## 依赖要求

确保安装了以下Python包：

```bash
pip install matplotlib numpy pandas
```

## 输出示例

### 控制台输出
```
性能对比分析结果
================================================================================

【MinIO 应用】
--------------------------------------------------
平均执行时间 (秒):
  DynamicWasm: 7.9066
  MCP:         1.8884
  绝对差值:    6.0182
  相对差值:    +318.89%
  → DynamicWasm 比 MCP 慢 318.89%

平均吞吐量:
  DynamicWasm: 0.2740
  MCP:         0.5304
  绝对差值:    -0.2564
  相对差值:    -48.35%
  → DynamicWasm 比 MCP 低 48.35%
...
```

### 图表说明
- 蓝色条形图代表DynamicWasm的性能指标
- 红色条形图代表MCP的性能指标
- 每个图表都包含数值标签，便于精确对比

## 注意事项

1. 确保测试结果JSON文件格式正确
2. 如果某个应用的测试结果文件缺失，工具会显示警告但继续分析其他应用
3. 图表使用中文字体，如果显示异常请检查系统字体配置
4. 输出目录会自动创建，如果已存在同名文件会被覆盖

## 故障排除

### 常见问题

1. **找不到测试结果文件**
   - 检查目录路径是否正确
   - 确认JSON文件命名格式符合要求（应用名_时间戳.json）

2. **图表中文显示异常**
   - 确保系统安装了中文字体
   - 可以修改 `performance_analyzer.py` 中的字体设置

3. **依赖包缺失**
   - 运行 `pip install matplotlib numpy pandas` 安装所需包

4. **权限错误**
   - 确保对输出目录有写入权限
