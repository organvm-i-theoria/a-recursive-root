"""
Video Output System for AI Council Debates

Generates video streams from debate transcripts with:
- Agent avatars
- Text overlays
- Audio from TTS
- Real-time streaming
"""

import asyncio
import logging
from typing import Optional, Dict, List, Any, Callable
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VideoFormat(Enum):
    """Video output formats"""
    MP4 = "mp4"
    WEBM = "webm"
    FLV = "flv"  # For RTMP streaming
    HLS = "hls"  # For adaptive streaming


class VideoResolution(Enum):
    """Standard video resolutions"""
    HD_720P = (1280, 720)
    HD_1080P = (1920, 1080)
    HD_1440P = (2560, 1440)
    UHD_4K = (3840, 2160)


@dataclass
class VideoConfig:
    """Video generation configuration"""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    format: VideoFormat = VideoFormat.MP4
    bitrate: str = "4M"
    audio_bitrate: str = "192k"
    codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "medium"  # ultrafast, superfast, fast, medium, slow
    output_dir: str = "./output/videos"


@dataclass
class DebateFrame:
    """Single frame in debate video"""
    timestamp: float
    agent_id: str
    agent_name: str
    text: str
    audio_path: Optional[str] = None
    avatar_path: Optional[str] = None
    round_number: int = 0
    message_type: str = "discussion"  # opening, discussion, vote


class VideoRenderer(ABC):
    """Abstract base for video renderers"""

    def __init__(self, config: VideoConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def render_frame(self, frame: DebateFrame) -> bytes:
        """Render a single frame"""
        pass

    @abstractmethod
    async def create_video(
        self,
        frames: List[DebateFrame],
        output_path: str
    ) -> str:
        """Create complete video from frames"""
        pass


class FFmpegVideoRenderer(VideoRenderer):
    """
    Video renderer using FFmpeg

    Requires: ffmpeg installed
    """

    def __init__(self, config: VideoConfig):
        super().__init__(config)
        self._verify_ffmpeg()

    def _verify_ffmpeg(self):
        """Check if FFmpeg is available"""
        import shutil
        if not shutil.which("ffmpeg"):
            raise RuntimeError(
                "FFmpeg not found. Install with: apt-get install ffmpeg "
                "or brew install ffmpeg"
            )
        logger.info("FFmpeg found")

    async def render_frame(self, frame: DebateFrame) -> bytes:
        """Generate image frame with text overlay"""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            logger.error("PIL not installed. Install with: pip install pillow")
            raise

        # Create blank frame
        img = Image.new('RGB', (self.config.width, self.config.height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)

        # Load fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            # Fallback to default
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Draw header
        header_height = 100
        draw.rectangle([(0, 0), (self.config.width, header_height)], fill='#16213e')
        draw.text(
            (self.config.width // 2, header_height // 2),
            "AI COUNCIL DEBATE",
            font=title_font,
            fill='#00d9ff',
            anchor='mm'
        )

        # Draw agent info
        agent_y = header_height + 50
        draw.text(
            (50, agent_y),
            f"🎤 {frame.agent_name}",
            font=text_font,
            fill='#ffffff'
        )

        # Draw round/type info
        draw.text(
            (self.config.width - 250, agent_y),
            f"Round {frame.round_number} • {frame.message_type.capitalize()}",
            font=small_font,
            fill='#888888'
        )

        # Draw text content (wrapped)
        content_y = agent_y + 80
        margin = 100
        max_width = self.config.width - (2 * margin)

        # Word wrap
        words = frame.text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=text_font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw lines
        line_height = 50
        for i, line in enumerate(lines[:10]):  # Max 10 lines
            draw.text(
                (margin, content_y + (i * line_height)),
                line,
                font=text_font,
                fill='#e0e0e0'
            )

        # Draw footer
        footer_y = self.config.height - 50
        draw.rectangle(
            [(0, footer_y), (self.config.width, self.config.height)],
            fill='#16213e'
        )
        timestamp_str = datetime.fromtimestamp(frame.timestamp).strftime("%H:%M:%S")
        draw.text(
            (self.config.width // 2, footer_y + 25),
            timestamp_str,
            font=small_font,
            fill='#888888',
            anchor='mm'
        )

        # Convert to bytes
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    async def create_video(
        self,
        frames: List[DebateFrame],
        output_path: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> str:
        """Create video from frames using FFmpeg"""
        import subprocess
        import tempfile

        logger.info(f"Creating video with {len(frames)} frames")

        # Create temp directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Render all frames
            for i, frame in enumerate(frames):
                frame_img = await self.render_frame(frame)
                frame_path = temp_path / f"frame_{i:06d}.png"

                with open(frame_path, 'wb') as f:
                    f.write(frame_img)

                if progress_callback:
                    progress = (i + 1) / len(frames) * 0.5  # First 50% is frame rendering
                    progress_callback(progress)

            # Create concat list with durations
            concat_file = temp_path / "concat.txt"
            with open(concat_file, 'w') as f:
                for i in range(len(frames)):
                    # Calculate duration for this frame
                    if i < len(frames) - 1:
                        duration = frames[i + 1].timestamp - frames[i].timestamp
                    else:
                        duration = 3.0  # Default for last frame

                    f.write(f"file 'frame_{i:06d}.png'\n")
                    f.write(f"duration {duration}\n")

                # Add last frame again for proper ending
                f.write(f"file 'frame_{len(frames) - 1:06d}.png'\n")

            # Build FFmpeg command
            output_file = self.output_dir / output_path
            output_file.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c:v', self.config.codec,
                '-preset', self.config.preset,
                '-b:v', self.config.bitrate,
                '-pix_fmt', 'yuv420p',
                '-y',  # Overwrite output
                str(output_file)
            ]

            # Add audio if available
            if frames[0].audio_path:
                # Create audio concat file
                audio_concat = temp_path / "audio_concat.txt"
                with open(audio_concat, 'w') as f:
                    for frame in frames:
                        if frame.audio_path and Path(frame.audio_path).exists():
                            f.write(f"file '{frame.audio_path}'\n")

                # Modify command to include audio
                cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(concat_file),
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(audio_concat),
                    '-c:v', self.config.codec,
                    '-preset', self.config.preset,
                    '-b:v', self.config.bitrate,
                    '-c:a', self.config.audio_codec,
                    '-b:a', self.config.audio_bitrate,
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    str(output_file)
                ]

            # Run FFmpeg
            logger.info(f"Running FFmpeg: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                raise RuntimeError(f"FFmpeg failed with code {process.returncode}")

            if progress_callback:
                progress_callback(1.0)

            logger.info(f"Video created: {output_file}")
            return str(output_file)


class StreamingVideoRenderer(VideoRenderer):
    """
    Streaming video renderer for live output

    Supports RTMP, HLS, and other streaming protocols
    """

    def __init__(self, config: VideoConfig, stream_url: str):
        super().__init__(config)
        self.stream_url = stream_url
        self.process: Optional[asyncio.subprocess.Process] = None

    async def start_stream(self):
        """Start streaming output"""
        import subprocess

        cmd = [
            'ffmpeg',
            '-f', 'image2pipe',
            '-framerate', str(self.config.fps),
            '-i', '-',  # Read from stdin
            '-c:v', self.config.codec,
            '-preset', 'ultrafast',  # Use fastest for streaming
            '-b:v', self.config.bitrate,
            '-pix_fmt', 'yuv420p',
            '-f', 'flv',  # For RTMP
            self.stream_url
        ]

        logger.info(f"Starting stream: {self.stream_url}")

        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def render_frame(self, frame: DebateFrame) -> bytes:
        """Render frame (same as FFmpegVideoRenderer)"""
        # Reuse FFmpegVideoRenderer's implementation
        renderer = FFmpegVideoRenderer(self.config)
        return await renderer.render_frame(frame)

    async def stream_frame(self, frame: DebateFrame):
        """Send frame to stream"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Stream not started")

        frame_data = await self.render_frame(frame)
        self.process.stdin.write(frame_data)
        await self.process.stdin.drain()

    async def stop_stream(self):
        """Stop streaming"""
        if self.process and self.process.stdin:
            self.process.stdin.close()
            await self.process.wait()
            logger.info("Stream stopped")

    async def create_video(self, frames: List[DebateFrame], output_path: str) -> str:
        """Stream all frames"""
        await self.start_stream()

        try:
            for frame in frames:
                await self.stream_frame(frame)
                # Respect framerate
                await asyncio.sleep(1.0 / self.config.fps)
        finally:
            await self.stop_stream()

        return self.stream_url


class VideoManager:
    """High-level video generation manager"""

    def __init__(self, config: VideoConfig):
        self.config = config
        self.renderer: Optional[VideoRenderer] = None

    def create_renderer(self, streaming: bool = False, stream_url: str = "") -> VideoRenderer:
        """Create appropriate renderer"""
        if streaming:
            if not stream_url:
                raise ValueError("stream_url required for streaming")
            self.renderer = StreamingVideoRenderer(self.config, stream_url)
        else:
            self.renderer = FFmpegVideoRenderer(self.config)

        return self.renderer

    async def create_debate_video(
        self,
        debate_transcript: List[Dict[str, Any]],
        audio_files: Dict[str, str],
        output_name: str,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> str:
        """
        Create video from debate transcript

        Args:
            debate_transcript: List of message dicts
            audio_files: Mapping of message_id -> audio_file_path
            output_name: Output filename
            progress_callback: Progress callback (0.0 to 1.0)

        Returns:
            Path to generated video
        """
        if not self.renderer:
            self.renderer = self.create_renderer()

        # Convert transcript to frames
        frames = []
        current_time = 0.0

        for msg in debate_transcript:
            # Determine duration from audio or estimate
            audio_path = audio_files.get(msg.get('message_id'))
            duration = 5.0  # Default duration

            if audio_path and Path(audio_path).exists():
                # Get actual audio duration
                duration = await self._get_audio_duration(audio_path)

            frame = DebateFrame(
                timestamp=current_time,
                agent_id=msg.get('agent_id', 'unknown'),
                agent_name=msg.get('agent_name', 'Agent'),
                text=msg.get('content', ''),
                audio_path=audio_path,
                round_number=msg.get('round', 0),
                message_type=msg.get('type', 'discussion')
            )
            frames.append(frame)
            current_time += duration

        # Create video
        output_path = await self.renderer.create_video(
            frames,
            output_name,
            progress_callback
        )

        return output_path

    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration using FFprobe"""
        import subprocess

        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            audio_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            logger.warning(f"Could not get duration for {audio_path}")
            return 5.0  # Default

    def get_stats(self) -> Dict[str, Any]:
        """Get video generation statistics"""
        return {
            "config": {
                "resolution": f"{self.config.width}x{self.config.height}",
                "fps": self.config.fps,
                "format": self.config.format.value,
                "bitrate": self.config.bitrate,
            },
            "output_dir": str(self.config.output_dir),
        }


# Convenience functions

def create_video_manager(
    resolution: VideoResolution = VideoResolution.HD_1080P,
    fps: int = 30,
    format: VideoFormat = VideoFormat.MP4,
    output_dir: str = "./output/videos"
) -> VideoManager:
    """Create video manager with standard config"""
    width, height = resolution.value
    config = VideoConfig(
        width=width,
        height=height,
        fps=fps,
        format=format,
        output_dir=output_dir
    )
    return VideoManager(config)
