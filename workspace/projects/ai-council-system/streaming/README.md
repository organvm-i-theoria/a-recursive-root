# AI Council System - Streaming Components

Audio and video generation for debate output.

## Components

### 1. Text-to-Speech (tts.py)

Multi-engine TTS system with automatic fallback.

**Supported Engines:**
- ElevenLabs (premium, realistic voices)
- pyttsx3 (local, offline)
- gTTS (Google Text-to-Speech, free)

**Usage:**

```python
from streaming.tts import TTSManager, TTSConfig, TTSEngine

# Create TTS manager
config = TTSConfig(
    engine=TTSEngine.ELEVENLABS,
    api_key="your-api-key"
)
tts = TTSManager(config)

# Synthesize single text
audio_path = await tts.synthesize(
    text="Hello from the AI Council",
    output_path="output.mp3",
    voice_id="21m00Tcm4TlvDq8ikWAM"  # ElevenLabs voice
)

# Synthesize entire debate
voice_mapping = {
    "agent_pragmatist": "21m00Tcm4TlvDq8ikWAM",
    "agent_idealist": "AZnzlk1XvdvUeBnXmlld",
}
audio_files = await tts.synthesize_debate(debate_transcript, voice_mapping)
```

### 2. Video Generation (video.py)

Create videos from debate transcripts with text overlays and audio.

**Features:**
- FFmpeg-based rendering
- Multiple resolutions (720p, 1080p, 4K)
- Live streaming support (RTMP, HLS)
- Text wrapping and formatting
- Agent avatars and overlays

**Usage:**

```python
from streaming.video import VideoManager, VideoResolution, VideoFormat

# Create video manager
video_mgr = create_video_manager(
    resolution=VideoResolution.HD_1080P,
    fps=30,
    format=VideoFormat.MP4
)

# Generate video from debate
video_path = await video_mgr.create_debate_video(
    debate_transcript=transcript,
    audio_files=audio_files,
    output_name="debate_001.mp4",
    progress_callback=lambda p: print(f"Progress: {p*100:.1f}%")
)

print(f"Video created: {video_path}")
```

### 3. Live Streaming

Stream debates in real-time to platforms like YouTube, Twitch, etc.

**Usage:**

```python
from streaming.video import StreamingVideoRenderer, VideoConfig

# Configure streaming
config = VideoConfig(
    width=1920,
    height=1080,
    fps=30,
    bitrate="4M"
)

# Create streaming renderer
renderer = StreamingVideoRenderer(
    config,
    stream_url="rtmp://live.youtube.com/app/YOUR_STREAM_KEY"
)

# Start streaming
await renderer.start_stream()

# Send frames in real-time
for frame in debate_frames:
    await renderer.stream_frame(frame)
    await asyncio.sleep(1.0 / config.fps)

await renderer.stop_stream()
```

## Installation

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg libespeak1 portaudio19-dev
```

**macOS:**
```bash
brew install ffmpeg portaudio espeak
```

### Python Dependencies

```bash
pip install elevenlabs gtts pyttsx3 pillow
```

## Configuration

### TTS Configuration

```yaml
tts:
  engine: "elevenlabs"  # or pyttsx3, gtts
  api_key: "your-elevenlabs-api-key"
  default_voice: "21m00Tcm4TlvDq8ikWAM"
  output_format: "mp3"
  sample_rate: 44100
  fallback_engines:
    - "pyttsx3"
    - "gtts"
```

### Video Configuration

```yaml
streaming:
  video:
    width: 1920
    height: 1080
    fps: 30
    format: "mp4"
    bitrate: "4M"
    codec: "libx264"
    preset: "medium"
  audio:
    bitrate: "192k"
    codec: "aac"
  output_dir: "./output/videos"
```

## ElevenLabs Setup

1. Sign up at https://elevenlabs.io
2. Get API key from dashboard
3. Choose voices from Voice Library
4. Set in config:

```python
config = TTSConfig(
    engine=TTSEngine.ELEVENLABS,
    api_key="your-api-key",
    voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
)
```

**Popular Voices:**
- Rachel: `21m00Tcm4TlvDq8ikWAM`
- Domi: `AZnzlk1XvdvUeBnXmlld`
- Bella: `EXAVITQu4vr4xnSDxMaL`
- Antoni: `ErXwobaYiN019PkySvjV`

## RTMP Streaming

### YouTube Live

1. Enable live streaming in YouTube Studio
2. Get stream key from "Go Live" page
3. Use URL:

```python
stream_url = "rtmp://a.rtmp.youtube.com/live2/YOUR_STREAM_KEY"
```

### Twitch

1. Get stream key from Twitch dashboard
2. Use URL:

```python
stream_url = "rtmp://live.twitch.tv/app/YOUR_STREAM_KEY"
```

### Custom RTMP Server

Use nginx-rtmp:

```nginx
rtmp {
    server {
        listen 1935;
        application live {
            live on;
            record off;
        }
    }
}
```

Stream URL: `rtmp://your-server:1935/live/debate`

## Video Formats

### MP4 (Default)
- Best compatibility
- Good compression
- Suitable for upload/download

### WebM
- Web-optimized
- Smaller file size
- Good for browser playback

### HLS
- Adaptive streaming
- Mobile-friendly
- Requires segmented output

### FLV
- RTMP streaming
- Live broadcasts
- Lower latency

## Performance

### Rendering Speed

- 720p: ~1x realtime (30fps)
- 1080p: ~0.5x realtime (15fps)
- 4K: ~0.2x realtime (6fps)

### Optimization Tips

1. Use `preset=ultrafast` for live streaming
2. Use `preset=slow` for best quality offline
3. Lower bitrate for bandwidth constraints
4. Use GPU encoding if available (h264_nvenc)

## Examples

### Basic Debate Video

```python
import asyncio
from streaming.tts import TTSManager, TTSConfig
from streaming.video import create_video_manager, VideoResolution

async def create_debate_video():
    # TTS setup
    tts_config = TTSConfig(engine="pyttsx3")  # Use offline engine
    tts = TTSManager(tts_config)

    # Generate audio
    transcript = [
        {"agent_id": "agent_1", "content": "I believe we should..."},
        {"agent_id": "agent_2", "content": "However, we must consider..."},
    ]

    audio_files = {}
    for i, msg in enumerate(transcript):
        path = await tts.synthesize(
            msg["content"],
            output_path=f"audio_{i}.mp3"
        )
        audio_files[str(i)] = path

    # Create video
    video_mgr = create_video_manager(resolution=VideoResolution.HD_720P)
    video_path = await video_mgr.create_debate_video(
        debate_transcript=transcript,
        audio_files=audio_files,
        output_name="my_debate.mp4"
    )

    print(f"✅ Video created: {video_path}")

asyncio.run(create_debate_video())
```

### Live Streaming

```python
async def stream_debate_live():
    from streaming.video import StreamingVideoRenderer, VideoConfig

    config = VideoConfig(width=1280, height=720, fps=30)
    renderer = StreamingVideoRenderer(
        config,
        stream_url="rtmp://live.twitch.tv/app/YOUR_KEY"
    )

    await renderer.start_stream()

    # Stream debate frames as they're generated
    async for frame in generate_debate_frames():
        await renderer.stream_frame(frame)

    await renderer.stop_stream()

asyncio.run(stream_debate_live())
```

## Troubleshooting

### FFmpeg Not Found

Install FFmpeg:

```bash
# Ubuntu
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

### Audio Issues

If pyttsx3 fails:

```bash
# Install espeak
sudo apt-get install espeak libespeak-dev

# Or use gTTS as fallback
```

### Memory Issues

For long debates, process in chunks:

```python
# Process debate in 10-minute segments
segment_duration = 600  # seconds
for segment in split_debate(transcript, segment_duration):
    await video_mgr.create_debate_video(segment, ...)
```

### Streaming Latency

Reduce latency with:

```python
config = VideoConfig(
    preset="ultrafast",
    fps=24,  # Lower FPS
    bitrate="2M"  # Lower bitrate
)
```

## License

Part of AI Council System
