import os
import requests
import json

def load_translation_sources(file_path=None):
    if not file_path:
        file_path = os.path.join(os.path.dirname(__file__), "translation_sources.txt")
    sources = []
    mapping = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # 三列：name|api|api_config
                name, api, api_config_str = line.split("|")
                try:
                    api_config = json.loads(api_config_str)
                except:
                    api_config = {}
                sources.append(name)
                mapping[name] = {
                    "api": api,
                    "api_config": api_config
                }
    except Exception as e:
        print(f"读取翻译源文件失败: {e}")
    return sources, mapping


class TranslatorNode:

    @classmethod
    def INPUT_TYPES(cls):
        # 每次调用前重新加载最新文件
        sources, _ = load_translation_sources()
        return {
            "required": {
                "text": ("STRING",),
                "direction": (["zh2en", "en2zh"], {"default": "zh2en"}),
                "source": (sources, {"default": sources[0] if sources else ""})
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "translate"
    CATEGORY = "Text"

    @staticmethod
    def translate(text, direction, source):
        # 每次调用前加载最新配置
        _, source_map = load_translation_sources()
        src_info = source_map.get(source)
        if not src_info:
            return "未找到翻译源配置"
        #texts = lambda text: [seg for part in text.split(",") for seg in ([part] if re.fullmatch(r"[A-Za-z0-9 ]+", part.strip()) else part.strip().split()) if seg]
        #texts = [t.strip() for t in text.replace(",", " ").split() if t.strip()]
        texts = [t.strip() for t in text.split(",") if t.strip()]
        api = src_info["api"]
        api_config = src_info.get("api_config", {})

        payload = {
            "texts": texts,
            "from_lang": "zh_CN" if direction == "zh2en" else "en_US",
            "to_lang": "en_US" if direction == "zh2en" else "zh_CN",
            "api": api,
            "api_config": api_config
        }
        print("===== 翻译接口 payload =====")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("============================")
        try:
            url = "http://xx.xx.xx.142:17860/physton_prompt/translates"
            response = requests.post(url, json=payload,proxies={"http": None, "https": None}, timeout=10)
            response.raise_for_status()
            result = response.json()
            print("===== 接口返回 JSON =====")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("=========================")
            re = ", ".join(result.get("translated_text", []))
            print("类型:", type(re))
            print("内容:", re)
            return (re,)
        except Exception as e:
            return f"翻译失败: {e}"
