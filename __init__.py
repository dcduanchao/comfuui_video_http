from .video_upload_node import VideoUploadNode
from .translator_node import TranslatorNode 
# 如果以后加其他上传节点，只需要 import 并加入下面映射
# from .image_upload_node import ImageUploadNode
# from .audio_upload_node import AudioUploadNode

NODE_CLASS_MAPPINGS = {
    "Video Upload Node": VideoUploadNode,
    "Translator Node": TranslatorNode,
}
