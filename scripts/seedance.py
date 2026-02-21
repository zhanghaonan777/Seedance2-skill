#!/usr/bin/env python3
"""
Seedance 视频生成 CLI（Volcengine Ark API）
用法见本 skill 的 SKILL.md「API 生成」一节。

  python3 seedance.py create --prompt "描述" [options]
  python3 seedance.py create --prompt "描述" --image img.jpg [options]
  python3 seedance.py create --prompt "描述" --image first.jpg --last-frame last.jpg [options]
  python3 seedance.py create --prompt "描述" --ref-images ref1.jpg ref2.jpg [options]
  python3 seedance.py create --prompt "描述" --video motion_ref.mp4 [options]
  python3 seedance.py create --prompt "描述" --audio bgm.mp3 [options]
  python3 seedance.py create --draft-task-id <task_id> [options]
  python3 seedance.py status <task_id>
  python3 seedance.py wait <task_id> [--interval 15] [--download DIR]
  python3 seedance.py list [--status succeeded] [--page 1] [--page-size 10]
  python3 seedance.py delete <task_id>
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
DEFAULT_MODEL = "doubao-seedance-2-0-260128"


def get_api_key():
    key = os.environ.get("ARK_API_KEY")
    if not key:
        print("Error: ARK_API_KEY environment variable is not set.", file=sys.stderr)
        print("Set it with: export ARK_API_KEY='your-api-key-here'", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(method, url, data=None):
    """Make an API request and return parsed JSON response."""
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            if resp_body:
                return json.loads(resp_body)
            return {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get("error", {}).get("message", error_body)
        except json.JSONDecodeError:
            error_msg = error_body
        print(f"API Error (HTTP {e.code}): {error_msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def image_to_data_url(image_path):
    """Convert a local image file to a base64 data URL."""
    p = Path(image_path)
    if not p.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    ext = p.suffix.lower().lstrip(".")
    mime_map = {
        "jpg": "jpeg", "jpeg": "jpeg", "png": "png",
        "webp": "webp", "bmp": "bmp", "tiff": "tiff",
        "tif": "tiff", "gif": "gif", "heic": "heic", "heif": "heif",
    }
    mime_ext = mime_map.get(ext, ext)

    file_size = p.stat().st_size
    if file_size > 30 * 1024 * 1024:
        print(f"Error: Image file too large ({file_size / 1024 / 1024:.1f} MB). Max 30 MB.", file=sys.stderr)
        sys.exit(1)

    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    return f"data:image/{mime_ext};base64,{b64}"


def resolve_image(image_input):
    """Resolve image input to a URL or data URL. Accepts URL or local file path."""
    if image_input.startswith(("http://", "https://", "data:")):
        return image_input
    return image_to_data_url(image_input)


def file_to_data_url(file_path, media_type):
    """Convert a local file to a base64 data URL. media_type: 'video' or 'audio'."""
    p = Path(file_path)
    if not p.exists():
        print(f"Error: {media_type.title()} file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    max_size = {"video": 50, "audio": 15}.get(media_type, 50)
    file_size = p.stat().st_size
    if file_size > max_size * 1024 * 1024:
        print(f"Error: {media_type.title()} file too large ({file_size / 1024 / 1024:.1f} MB). Max {max_size} MB.", file=sys.stderr)
        sys.exit(1)

    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        ext_map = {
            "mp4": "video/mp4", "mov": "video/quicktime", "webm": "video/webm",
            "mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg",
        }
        mime = ext_map.get(p.suffix.lower().lstrip("."), f"{media_type}/octet-stream")

    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    return f"data:{mime};base64,{b64}"


def resolve_media(media_input, media_type):
    """Resolve media input (video/audio) to URL or data URL."""
    if media_input.startswith(("http://", "https://", "data:")):
        return media_input
    return file_to_data_url(media_input, media_type)


def cmd_create(args):
    """Create a video generation task."""
    content = []

    if args.draft_task_id:
        content.append({
            "type": "draft_task",
            "draft_task": {"id": args.draft_task_id}
        })
    else:
        if args.prompt:
            content.append({"type": "text", "text": args.prompt})

        if args.ref_images:
            for img in args.ref_images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": resolve_image(img)},
                    "role": "reference_image"
                })
        elif args.image:
            content.append({
                "type": "image_url",
                "image_url": {"url": resolve_image(args.image)},
                "role": "first_frame"
            })
            if args.last_frame:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": resolve_image(args.last_frame)},
                    "role": "last_frame"
                })

        if args.video:
            for v in args.video:
                content.append({
                    "type": "video_url",
                    "video_url": {"url": resolve_media(v, "video")}
                })

        if args.audio:
            for a in args.audio:
                content.append({
                    "type": "audio_url",
                    "audio_url": {"url": resolve_media(a, "audio")}
                })

    if not content:
        print("Error: Must provide --prompt, --image, --video, --audio, or --draft-task-id.", file=sys.stderr)
        sys.exit(1)

    body = {
        "model": args.model,
        "content": content,
    }

    if args.ratio:
        body["ratio"] = args.ratio
    if args.duration is not None:
        body["duration"] = args.duration
    if args.resolution:
        body["resolution"] = args.resolution
    if args.seed is not None:
        body["seed"] = args.seed
    if args.camera_fixed is not None:
        body["camera_fixed"] = args.camera_fixed
    if args.watermark is not None:
        body["watermark"] = args.watermark
    if args.generate_audio is not None:
        body["generate_audio"] = args.generate_audio
    if args.draft is not None:
        body["draft"] = args.draft
    if args.return_last_frame is not None:
        body["return_last_frame"] = args.return_last_frame
    if args.service_tier:
        body["service_tier"] = args.service_tier
    if getattr(args, 'frames', None) is not None:
        body["frames"] = args.frames
    if getattr(args, 'execution_expires_after', None) is not None:
        body["execution_expires_after"] = args.execution_expires_after
    if getattr(args, 'callback_url', None):
        body["callback_url"] = args.callback_url

    result = api_request("POST", BASE_URL, body)
    task_id = result.get("id", "")

    print(json.dumps({"task_id": task_id, "status": "created", "response": result}, indent=2))

    if args.wait:
        return cmd_wait_logic(task_id, args.interval or 15, args.download)

    return task_id


def cmd_status(args):
    """Query task status."""
    url = f"{BASE_URL}/{args.task_id}"
    result = api_request("GET", url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def cmd_wait_logic(task_id, interval=15, download_dir=None):
    """Wait for task completion, optionally download result."""
    url = f"{BASE_URL}/{task_id}"
    print(f"Waiting for task {task_id} to complete (polling every {interval}s)...")

    while True:
        result = api_request("GET", url)
        status = result.get("status", "unknown")

        if status == "succeeded":
            video_url = result.get("content", {}).get("video_url", "")
            last_frame_url = result.get("content", {}).get("last_frame_url")
            duration = result.get("duration", "?")
            resolution = result.get("resolution", "?")
            ratio = result.get("ratio", "?")

            print(f"\nVideo generation succeeded!")
            print(f"  Duration: {duration}s | Resolution: {resolution} | Ratio: {ratio}")
            print(f"  Video URL: {video_url}")
            if last_frame_url:
                print(f"  Last Frame URL: {last_frame_url}")

            if download_dir and video_url:
                download_path = Path(download_dir).expanduser()
                download_path.mkdir(parents=True, exist_ok=True)
                filename = f"seedance_{task_id}_{int(time.time())}.mp4"
                filepath = download_path / filename

                print(f"\nDownloading video to {filepath}...")
                try:
                    urllib.request.urlretrieve(video_url, str(filepath))
                    print(f"Saved to: {filepath}")

                    if sys.platform == "darwin":
                        os.system(f'open "{filepath}"')
                except Exception as e:
                    print(f"Download failed: {e}", file=sys.stderr)

            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result

        elif status == "failed":
            error = result.get("error", {})
            print(f"\nVideo generation failed!")
            print(f"  Error: {error.get('code', 'unknown')} - {error.get('message', 'Unknown error')}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(1)

        elif status == "expired":
            print(f"\nVideo generation task expired.")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            sys.exit(1)

        else:
            print(f"  Status: {status}...", flush=True)
            time.sleep(interval)


def cmd_wait(args):
    """Wait for task completion."""
    return cmd_wait_logic(args.task_id, args.interval, args.download)


def cmd_list(args):
    """List video generation tasks."""
    params = []
    if args.page:
        params.append(f"page_num={args.page}")
    if args.page_size:
        params.append(f"page_size={args.page_size}")
    if args.status:
        params.append(f"filter.status={args.status}")

    url = BASE_URL
    if params:
        url += "?" + "&".join(params)

    result = api_request("GET", url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def cmd_delete(args):
    """Cancel or delete a task."""
    url = f"{BASE_URL}/{args.task_id}"
    api_request("DELETE", url)
    print(f"Task {args.task_id} cancelled/deleted successfully.")


def parse_bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("true", "1", "yes"):
        return True
    if v.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean expected, got '{v}'")


def main():
    parser = argparse.ArgumentParser(description="Seedance Video Generation CLI (Volcengine Ark)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_create = subparsers.add_parser("create", help="Create a video generation task")
    p_create.add_argument("--prompt", "-p", help="Text prompt describing the video")
    p_create.add_argument("--image", "-i", help="First frame image (URL or local file path)")
    p_create.add_argument("--last-frame", help="Last frame image (URL or local file path)")
    p_create.add_argument("--ref-images", nargs="+", help="Reference images (1-9 URLs or paths)")
    p_create.add_argument("--video", nargs="+", help="Reference videos (URL or local file, max 3, Seedance 2.0)")
    p_create.add_argument("--audio", nargs="+", help="Reference audio (URL or local file, max 3, Seedance 2.0)")
    p_create.add_argument("--draft-task-id", help="Draft task ID to generate final video from")
    p_create.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    p_create.add_argument("--ratio", choices=["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"], help="Aspect ratio")
    p_create.add_argument("--duration", "-d", type=int, help="Duration in seconds (4-15, or -1 for auto)")
    p_create.add_argument("--resolution", "-r", choices=["480p", "720p", "1080p"], help="Resolution")
    p_create.add_argument("--seed", type=int, help="Random seed (-1 for random)")
    p_create.add_argument("--camera-fixed", type=parse_bool, help="Fix camera position (true/false)")
    p_create.add_argument("--watermark", type=parse_bool, help="Add watermark (true/false)")
    p_create.add_argument("--generate-audio", type=parse_bool, help="Generate audio (true/false)")
    p_create.add_argument("--draft", type=parse_bool, help="Draft/preview mode (true/false, 1.5 Pro)")
    p_create.add_argument("--return-last-frame", type=parse_bool, help="Return last frame URL (true/false)")
    p_create.add_argument("--service-tier", choices=["default", "flex"], help="Service tier (flex = offline, 50%% cheaper)")
    p_create.add_argument("--frames", type=int, help="Exact frame count (25+4n, range 29-289, 1.0 models only)")
    p_create.add_argument("--execution-expires-after", type=int, help="Task timeout in seconds (3600-259200)")
    p_create.add_argument("--callback-url", help="Webhook URL for task status notifications")
    p_create.add_argument("--wait", "-w", action="store_true", help="Wait for completion after creating")
    p_create.add_argument("--interval", type=int, default=15, help="Poll interval in seconds (default: 15)")
    p_create.add_argument("--download", help="Download directory (e.g. ~/Desktop)")

    p_status = subparsers.add_parser("status", help="Query task status")
    p_status.add_argument("task_id", help="Task ID to query")

    p_wait = subparsers.add_parser("wait", help="Wait for task completion")
    p_wait.add_argument("task_id", help="Task ID to wait for")
    p_wait.add_argument("--interval", type=int, default=15, help="Poll interval in seconds (default: 15)")
    p_wait.add_argument("--download", help="Download directory (e.g. ~/Desktop)")

    p_list = subparsers.add_parser("list", help="List video generation tasks")
    p_list.add_argument("--status", choices=["queued", "running", "cancelled", "succeeded", "failed", "expired"])
    p_list.add_argument("--page", type=int, default=1)
    p_list.add_argument("--page-size", type=int, default=10)

    p_delete = subparsers.add_parser("delete", help="Cancel or delete a task")
    p_delete.add_argument("task_id", help="Task ID to cancel/delete")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "create": cmd_create,
        "status": cmd_status,
        "wait": cmd_wait,
        "list": cmd_list,
        "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
