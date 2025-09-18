from .video_upload_node import VideoUploadNode

# 如果以后加其他上传节点，只需要 import 并加入下面映射
# from .image_upload_node import ImageUploadNode
# from .audio_upload_node import AudioUploadNode

NODE_CLASS_MAPPINGS = {
    "Video Upload Node": VideoUploadNode,
    # "Image Upload Node": ImageUploadNode,
    # "Audio Upload Node": AudioUploadNode,
}
