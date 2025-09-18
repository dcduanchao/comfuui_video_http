import os
import threading
import tempfile
import requests

class VideoUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),  # 直接连接“创建视频”或“保存视频”节点输出
                "target_url": ("STRING", {"default": "http://127.0.0.1:8080/upload"}),
                "async_mode": ("BOOLEAN", {"default": True}),  # UI 上显示开关
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "upload_video"
    CATEGORY = "Upload"

    def _get_video_path(self, video):
        """
        获取可上传的视频文件路径：
        1. VideoFromFile 直接返回已有文件路径
        2. VideoFromComponents 调用 save_to 保存成临时文件
        """
        # VideoFromFile
        if hasattr(video, "_VideoFromFile__file"):
            path = getattr(video, "_VideoFromFile__file")
            if path and os.path.isfile(path):
                return path

        # VideoFromComponents
        if hasattr(video, "save_to"):
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            video.save_to(temp_path)
            return temp_path

        # fallback: 尝试常见属性
        for attr in ["file_path", "path", "filename", "name"]:
            if hasattr(video, attr):
                val = getattr(video, attr)
                if val and os.path.isfile(val):
                    return val

        return None

    def _upload(self, path, target_url):
        """
        执行上传，返回 Spring Boot 完整响应
        上传完成后删除临时文件（如果是临时生成）
        """
        result = ""
        try:
            with open(path, "rb") as f:
                files = {"file": (os.path.basename(path), f, "video/mp4")}
                r = requests.post(target_url, files=files)
                result = r.text
        except Exception as e:
            result = f"上传失败: {e}"
        finally:
            # 如果是临时文件，上传完成后删除
            if "tmp" in path or "tmp" in os.path.dirname(path):
                try:
                    os.remove(path)
                    print(f"[VideoUploadNode] 删除临时文件: {path}")
                except Exception as e:
                    print(f"[VideoUploadNode] 删除临时文件失败: {e}")
        return result

    def upload_video(self, video, target_url, async_mode=True):
        print("DEBUG video object:", video)
        print("DEBUG video object attributes:", dir(video))
        path = self._get_video_path(video)
        if not path:
            return (f"无法识别视频文件: {video}",)

        if async_mode:
            # 异步上传
            def run():
                result = self._upload(path, target_url)
                print(f"[VideoUploadNode] 异步上传完成: {result}")

            threading.Thread(target=run, daemon=True).start()
            return ("上传已启动 (异步)",)
        else:
            # 同步上传
            result = self._upload(path, target_url)
            return (result,)
