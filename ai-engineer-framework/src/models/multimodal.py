"""
多模态AI处理框架

支持文本、图像、音频、视频等多种媒体类型的处理和理解
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncGenerator
from enum import Enum
import base64
import io
import time
from pathlib import Path

from pydantic import BaseModel, Field, validator

from .llm import Message, ModelResponse, LLMProvider


class MediaType(str, Enum):
    """媒体类型"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    MIXED = "mixed"


class ImageFormat(str, Enum):
    """图像格式"""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"


class AudioFormat(str, Enum):
    """音频格式"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"


class VideoFormat(str, Enum):
    """视频格式"""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"
    MKV = "mkv"


@dataclass
class MediaContent:
    """媒体内容"""
    media_type: MediaType
    data: Union[str, bytes]  # base64编码的字符串或原始字节
    format: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    size: int = 0
    duration: Optional[float] = None  # 音频/视频时长
    dimensions: Optional[Tuple[int, int]] = None  # 图像/视频尺寸

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "media_type": self.media_type.value,
            "data": self.data if isinstance(self.data, str) else base64.b64encode(self.data).decode(),
            "format": self.format,
            "metadata": self.metadata,
            "size": self.size,
            "duration": self.duration,
            "dimensions": self.dimensions
        }


@dataclass
class MultimodalMessage:
    """多模态消息"""
    role: str
    content: List[MediaContent]
    text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def add_text(self, text: str) -> None:
        """添加文本内容"""
        if self.text:
            self.text += "\n" + text
        else:
            self.text = text

    def add_media(self, media: MediaContent) -> None:
        """添加媒体内容"""
        self.content.append(media)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "role": self.role,
            "text": self.text,
            "content": [media.to_dict() for media in self.content],
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


@dataclass
class MediaAnalysis:
    """媒体分析结果"""
    media_type: MediaType
    description: str
    confidence: float
    extracted_text: Optional[str] = None
    objects: List[Dict[str, Any]] = field(default_factory=list)
    features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultimodalConfig(BaseModel):
    """多模态处理配置"""
    # 图像处理配置
    vision_model: str = Field("gpt-4-vision-preview", description="视觉模型")
    max_image_size: int = Field(20 * 1024 * 1024, description="最大图像大小（字节）")
    supported_image_formats: List[ImageFormat] = Field(
        default=[ImageFormat.JPEG, ImageFormat.PNG, ImageFormat.GIF, ImageFormat.WEBP],
        description="支持的图像格式"
    )

    # 音频处理配置
    audio_model: str = Field("whisper-1", description="音频模型")
    max_audio_size: int = Field(25 * 1024 * 1024, description="最大音频大小（字节）")
    supported_audio_formats: List[AudioFormat] = Field(
        default=[AudioFormat.WAV, AudioFormat.MP3, AudioFormat.FLAC],
        description="支持的音频格式"
    )

    # 视频处理配置
    max_video_duration: int = Field(600, description="最大视频时长（秒）")
    supported_video_formats: List[VideoFormat] = Field(
        default=[VideoFormat.MP4, VideoFormat.MOV, VideoFormat.AVI],
        description="支持的视频格式"
    )

    # 通用配置
    enable_cache: bool = Field(True, description="是否启用缓存")
    max_concurrent_processing: int = Field(5, description="最大并发处理数")
    timeout: int = Field(300, description="处理超时时间（秒）")


class MediaProcessor(ABC):
    """媒体处理器抽象基类"""

    def __init__(self, config: MultimodalConfig):
        self.config = config
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """初始化处理器"""
        pass

    @abstractmethod
    async def process(self, media: MediaContent) -> MediaAnalysis:
        """处理媒体"""
        pass

    @abstractmethod
    def supports(self, media_type: MediaType, format: Optional[str] = None) -> bool:
        """检查是否支持该媒体类型和格式"""
        pass

    async def validate_media(self, media: MediaContent) -> bool:
        """验证媒体内容"""
        if media.media_type == MediaType.IMAGE:
            if media.size > self.config.max_image_size:
                raise ValueError(f"Image size exceeds limit: {media.size} > {self.config.max_image_size}")
            if media.format and media.format not in [f.value for f in self.config.supported_image_formats]:
                raise ValueError(f"Unsupported image format: {media.format}")

        elif media.media_type == MediaType.AUDIO:
            if media.size > self.config.max_audio_size:
                raise ValueError(f"Audio size exceeds limit: {media.size} > {self.config.max_audio_size}")
            if media.format and media.format not in [f.value for f in self.config.supported_audio_formats]:
                raise ValueError(f"Unsupported audio format: {media.format}")

        return True

    async def cleanup(self) -> None:
        """清理资源"""
        pass


class ImageProcessor(MediaProcessor):
    """图像处理器"""

    def __init__(self, config: MultimodalConfig, vision_llm: LLMProvider):
        super().__init__(config)
        self.vision_llm = vision_llm

    async def initialize(self) -> None:
        """初始化图像处理器"""
        await self.vision_llm.initialize()
        self._initialized = True

    def supports(self, media_type: MediaType, format: Optional[str] = None) -> bool:
        """检查是否支持图像格式"""
        return media_type == MediaType.IMAGE and (
            format is None or format in [f.value for f in self.config.supported_image_formats]
        )

    async def process(self, media: MediaContent) -> MediaAnalysis:
        """处理图像"""
        if not self._initialized:
            await self.initialize()

        await self.validate_media(media)

        # 构建多模态消息
        message = Message(
            role="user",
            content="请详细描述这张图像的内容，包括主要对象、场景、颜色、布局等。"
        )

        # 添加图像到消息（这里需要根据具体的LLM实现来调整）
        if isinstance(media.data, bytes):
            image_data = base64.b64encode(media.data).decode()
        else:
            image_data = media.data

        # 发送到视觉LLM
        response = await self.vision_llm.generate([message], image=image_data)

        return MediaAnalysis(
            media_type=MediaType.IMAGE,
            description=response.content,
            confidence=0.8,  # 这里可以根据实际模型输出来设置
            metadata={
                "model_used": self.config.vision_model,
                "processing_time": 0  # TODO: 实现计时
            }
        )


class AudioProcessor(MediaProcessor):
    """音频处理器"""

    def __init__(self, config: MultimodalConfig):
        super().__init__(config)
        self.whisper_model = None

    async def initialize(self) -> None:
        """初始化音频处理器"""
        try:
            import whisper
            self.whisper_model = whisper.load_model(self.config.audio_model)
            self._initialized = True
        except ImportError:
            raise ImportError("Whisper not installed. Please install it with: pip install whisper")

    def supports(self, media_type: MediaType, format: Optional[str] = None) -> bool:
        """检查是否支持音频格式"""
        return media_type == MediaType.AUDIO and (
            format is None or format in [f.value for f in self.config.supported_audio_formats]
        )

    async def process(self, media: MediaContent) -> MediaAnalysis:
        """处理音频"""
        if not self._initialized:
            await self.initialize()

        await self.validate_media(media)

        # 将音频数据保存到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=f".{media.format or 'wav'}", delete=False) as temp_file:
            if isinstance(media.data, bytes):
                temp_file.write(media.data)
            else:
                temp_file.write(base64.b64decode(media.data))
            temp_file_path = temp_file.name

        try:
            # 使用Whisper进行转录
            result = self.whisper_model.transcribe(temp_file_path)

            return MediaAnalysis(
                media_type=MediaType.AUDIO,
                description="音频转录完成",
                confidence=0.9,
                extracted_text=result["text"],
                metadata={
                    "language": result.get("language"),
                    "segments": result.get("segments", []),
                    "processing_time": 0  # TODO: 实现计时
                }
            )

        finally:
            # 清理临时文件
            import os
            try:
                os.unlink(temp_file_path)
            except:
                pass


class VideoProcessor(MediaProcessor):
    """视频处理器"""

    def __init__(self, config: MultimodalConfig, image_processor: ImageProcessor):
        super().__init__(config)
        self.image_processor = image_processor

    async def initialize(self) -> None:
        """初始化视频处理器"""
        await self.image_processor.initialize()
        self._initialized = True

    def supports(self, media_type: MediaType, format: Optional[str] = None) -> bool:
        """检查是否支持视频格式"""
        return media_type == MediaType.VIDEO and (
            format is None or format in [f.value for f in self.config.supported_video_formats]
        )

    async def process(self, media: MediaContent) -> MediaAnalysis:
        """处理视频"""
        if not self._initialized:
            await self.initialize()

        await self.validate_media(media)

        # 这里需要实现视频处理逻辑
        # 可以提取关键帧并进行图像分析
        # 可以提取音频并进行音频转录

        return MediaAnalysis(
            media_type=MediaType.VIDEO,
            description="视频处理完成",
            confidence=0.7,
            metadata={
                "duration": media.duration,
                "processing_time": 0  # TODO: 实现计时
            }
        )


class MultimodalProcessor:
    """多模态处理器"""

    def __init__(self, config: MultimodalConfig, llm_provider: LLMProvider):
        self.config = config
        self.llm_provider = llm_provider
        self.processors: Dict[MediaType, MediaProcessor] = {}
        self._cache: Dict[str, MediaAnalysis] = {}
        self._semaphore = asyncio.Semaphore(config.max_concurrent_processing)

    async def initialize(self) -> None:
        """初始化多模态处理器"""
        await self.llm_provider.initialize()

        # 初始化各种处理器
        self.processors[MediaType.IMAGE] = ImageProcessor(self.config, self.llm_provider)
        self.processors[MediaType.AUDIO] = AudioProcessor(self.config)
        self.processors[MediaType.VIDEO] = VideoProcessor(self.config, self.processors[MediaType.IMAGE])

        # 初始化所有处理器
        for processor in self.processors.values():
            await processor.initialize()

    async def process_message(self, message: MultimodalMessage) -> str:
        """处理多模态消息"""
        analyses = []

        # 并行处理所有媒体内容
        async with self._semaphore:
            tasks = []
            for media in message.content:
                task = self._process_single_media(media)
                tasks.append(task)

            if tasks:
                media_analyses = await asyncio.gather(*tasks)
                analyses.extend(media_analyses)

        # 构建增强的提示词
        enhanced_prompt = self._build_enhanced_prompt(message.text or "", analyses)

        # 发送给LLM
        llm_message = Message(role="user", content=enhanced_prompt)
        response = await self.llm_provider.generate([llm_message])

        return response.content

    async def _process_single_media(self, media: MediaContent) -> MediaAnalysis:
        """处理单个媒体内容"""
        # 检查缓存
        cache_key = self._generate_cache_key(media)
        if self.config.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # 获取对应的处理器
        processor = self.processors.get(media.media_type)
        if not processor or not processor.supports(media.media_type, media.format):
            raise ValueError(f"Unsupported media type: {media.media_type}")

        # 处理媒体
        analysis = await processor.process(media)

        # 缓存结果
        if self.config.enable_cache:
            self._cache[cache_key] = analysis

        return analysis

    def _build_enhanced_prompt(self, text: str, analyses: List[MediaAnalysis]) -> str:
        """构建增强的提示词"""
        prompt_parts = [text] if text else []

        for i, analysis in enumerate(analyses, 1):
            if analysis.media_type == MediaType.IMAGE:
                prompt_parts.append(f"图像{i}描述: {analysis.description}")
                if analysis.objects:
                    prompt_parts.append(f"图像{i}中的对象: {analysis.objects}")
            elif analysis.media_type == MediaType.AUDIO:
                prompt_parts.append(f"音频{i}转录: {analysis.extracted_text}")
            elif analysis.media_type == MediaType.VIDEO:
                prompt_parts.append(f"视频{i}分析: {analysis.description}")

        return "\n\n".join(prompt_parts)

    def _generate_cache_key(self, media: MediaContent) -> str:
        """生成缓存键"""
        import hashlib
        content = media.data if isinstance(media.data, str) else base64.b64encode(media.data).decode()
        key_str = f"{media.media_type.value}_{media.format}_{media.size}_{hashlib.md5(content.encode()).hexdigest()}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def analyze_media(self, media: MediaContent) -> MediaAnalysis:
        """分析单个媒体"""
        return await self._process_single_media(media)

    async def batch_process(self, media_list: List[MediaContent]) -> List[MediaAnalysis]:
        """批量处理媒体"""
        async with self._semaphore:
            tasks = [self._process_single_media(media) for media in media_list]
            return await asyncio.gather(*tasks)

    async def generate_with_media(
        self,
        prompt: str,
        media_contents: List[MediaContent],
        **kwargs
    ) -> str:
        """使用媒体内容生成回复"""
        # 创建多模态消息
        message = MultimodalMessage(role="user", text=prompt)
        for media in media_contents:
            message.add_media(media)

        # 处理并生成回复
        return await self.process_message(message)

    async def cleanup(self) -> None:
        """清理资源"""
        for processor in self.processors.values():
            await processor.cleanup()

        self._cache.clear()


# 工具函数
def create_media_content_from_file(file_path: Union[str, Path]) -> MediaContent:
    """从文件创建媒体内容"""
    file_path = Path(file_path)

    # 确定媒体类型
    extension = file_path.suffix.lower()
    if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
        media_type = MediaType.IMAGE
        format_type = extension[1:]  # 去掉点号
    elif extension in ['.wav', '.mp3', '.flac', '.ogg', '.m4a']:
        media_type = MediaType.AUDIO
        format_type = extension[1:]
    elif extension in ['.mp4', '.avi', '.mov', '.webm', '.mkv']:
        media_type = MediaType.VIDEO
        format_type = extension[1:]
    else:
        raise ValueError(f"Unsupported file format: {extension}")

    # 读取文件数据
    with open(file_path, 'rb') as f:
        data = f.read()

    # 创建媒体内容
    media = MediaContent(
        media_type=media_type,
        data=data,
        format=format_type,
        size=len(data),
        metadata={
            "filename": file_path.name,
            "original_path": str(file_path)
        }
    )

    # 如果是图像，获取尺寸信息
    if media_type == MediaType.IMAGE:
        try:
            from PIL import Image
            with Image.open(io.BytesIO(data)) as img:
                media.dimensions = img.size
        except:
            pass

    return media


def create_media_content_from_url(url: str, media_type: MediaType) -> MediaContent:
    """从URL创建媒体内容"""
    import httpx

    response = httpx.get(url)
    response.raise_for_status()

    # 从URL推断格式
    path_parts = url.split('.')
    format_type = path_parts[-1] if len(path_parts) > 1 else None

    return MediaContent(
        media_type=media_type,
        data=response.content,
        format=format_type,
        size=len(response.content),
        metadata={"source_url": url}
    )