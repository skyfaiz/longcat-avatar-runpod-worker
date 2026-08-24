# RunPod LongCat Worker

## 职责描述

把本机上传的人像、音频和提示词转换为 RunPod 队列任务，并调用 LongCat-Video-Avatar 1.5 INT8 生成 MP4。

## 能力清单

- 接收 HTTP(S) URL 或 data URI 输入
- 校验输入大小、分段数和分辨率
- 按需同步 LongCat 最小推理权重
- 通过 RunPod Serverless 返回 Base64 MP4

## 文件分工与协作

| 文件 | 职责 | 与其他文件的关系 |
| --- | --- | --- |
| `Dockerfile` | 构建 CUDA/PyTorch 推理镜像 | 安装官方 LongCat 与 Worker |
| `entrypoint.sh` | 容器启动入口 | 先同步权重，再启动 Handler |
| `sync_models.py` | 下载最小推理权重 | 写入持久化模型目录 |
| `handler.py` | 输入校验、推理和结果编码 | 调用官方 LongCat CLI |
| `test_handler.py` | 无 GPU 自检 | 验证输入边界 |

## 依赖与交互

- **依赖的模块**：官方 LongCat-Video、PyTorch 2.6、RunPod SDK、Hugging Face Hub
- **被依赖情况**：本机 `avatar_studio.backends` 调用 Endpoint
- **交互方式**：RunPod 队列 JSON；输入和输出使用 Base64
- **请求/响应规范**：`input` 必须包含 `image`、`audio`、`prompt`；成功响应包含 `video_base64`
- **错误约定**：非法输入抛出 `ValueError`，模型或推理失败抛出运行时错误，由 RunPod 标记任务失败

## 领域职责评价

Worker 保持为官方 CLI 的薄适配层，部署简单，但每个任务都会重新加载模型。吞吐量有明确需求后再改为常驻 Pipeline。

## 开发规范与注意事项

- 不把 API Key、用户素材或生成视频写入镜像
- 下载输入限制为 25MB，URL 只接受 HTTP(S)
- 模型目录必须使用 RunPod 持久卷，避免重复下载
- 默认单 GPU、INT8、蒸馏 8 步；修改参数后必须重新做 GPU 冒烟测试

## TODO

- [ ] 有稳定对象存储后改为 URL 输出，解除 Base64 结果大小限制
