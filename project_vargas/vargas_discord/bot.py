"""
Project Vargas — Discord Bot

Pure conversational interface. Zero commands. Every message goes to Vargas.
Vargas infers intent from natural language and decides how to respond.

Usage:
    python -m project_vargas.discord.bot
"""

import logging
import os
import sys
from pathlib import Path

import discord
from dotenv import load_dotenv

# Ensure project root is on path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.vargas_agent import VargasAgent

# Load environment variables from project root/.env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("vargas.discord")

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Vargas agent — initialized on ready
vargas: VargasAgent = None

# Discord message length limit
MAX_MSG_LENGTH = 2000


def split_response(text: str, max_len: int = MAX_MSG_LENGTH) -> list[str]:
    """Split a long response into chunks at paragraph breaks."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""

    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_len:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current.strip())
            # If a single paragraph is too long, split on sentences
            if len(para) > max_len:
                sentences = para.replace(". ", ".\n").split("\n")
                current = ""
                for sentence in sentences:
                    if len(current) + len(sentence) + 1 <= max_len:
                        current = f"{current} {sentence}" if current else sentence
                    else:
                        if current:
                            chunks.append(current.strip())
                        current = sentence
            else:
                current = para

    if current:
        chunks.append(current.strip())

    return chunks if chunks else [text[:max_len]]


# V2 — Track approval messages: message_id -> (channel_id, call_id)
pending_approvals: dict[int, tuple[str, str]] = {}


async def _approval_callback(channel_id: str, call_id: str, description: str):
    """Send an approval request to Discord and track it."""
    channel = client.get_channel(int(channel_id))
    if not channel:
        logger.warning("Approval callback: channel %s not found", channel_id)
        return
    msg = await channel.send(
        f"🔒 **Approval required:**\n{description}\n\n"
        f"React ✅ to approve or ❌ to reject."
    )
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    pending_approvals[msg.id] = (channel_id, call_id)


async def _progress_callback(channel_id: str, message: str):
    """Send a progress update to Discord."""
    channel = client.get_channel(int(channel_id))
    if channel:
        await channel.send(message)


@client.event
async def on_ready():
    global vargas
    logger.info("Logged in as %s (ID: %s)", client.user, client.user.id)
    logger.info("Connected to %d server(s)", len(client.guilds))
    for guild in client.guilds:
        logger.info("  - %s (%d members)", guild.name, guild.member_count)

    # Initialize Vargas agent
    try:
        vargas = VargasAgent()
        # V2 — Wire approval callback into executor
        vargas._executor.set_approval_callback(_approval_callback)
        # V2 — Override progress callback to send real Discord messages
        vargas._progress_callback = _progress_callback
        health = vargas.health_check()
        logger.info("Vargas online: %s", health)
    except Exception as e:
        logger.error("Failed to initialize Vargas: %s", e)
        vargas = None

    logger.info("Vargas is ready.")


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Handle approval reactions for V2 tool execution."""
    if payload.user_id == client.user.id:
        return  # Ignore our own reactions

    msg_id = payload.message_id
    if msg_id not in pending_approvals:
        return

    channel_id, call_id = pending_approvals[msg_id]
    emoji = str(payload.emoji)

    if emoji == "✅":
        vargas._executor.resolve_approval(channel_id, call_id, approved=True)
        del pending_approvals[msg_id]
        logger.info("Approval granted: %s", call_id)
    elif emoji == "❌":
        vargas._executor.resolve_approval(channel_id, call_id, approved=False)
        del pending_approvals[msg_id]
        logger.info("Approval rejected: %s", call_id)


@client.event
async def on_message(message: discord.Message):
    global vargas

    # Ignore own messages
    if message.author == client.user:
        return

    # Ignore bots
    if message.author.bot:
        return

    # V3 1C — DM support: use author ID as channel_id for direct messages
    if isinstance(message.channel, discord.DMChannel):
        effective_channel_id = str(message.author.id)
    else:
        effective_channel_id = str(message.channel.id)

    # Strip mention from content if present
    content = message.content
    if client.user in (message.mentions or []):
        content = content.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()

    # V3 1B — Blanket approval via natural language
    lower_content = content.lower().strip()
    if vargas and lower_content in ("blanket approve", "approve all", "blanket approval"):
        vargas._executor.grant_blanket_approval(effective_channel_id)
        await message.reply("Blanket approval granted for this channel. All gated operations will auto-approve until revoked.")
        return
    if vargas and lower_content in ("blanket revoke", "revoke approval", "revoke blanket"):
        vargas._executor.revoke_blanket_approval(effective_channel_id)
        await message.reply("Blanket approval revoked. Gated operations will require individual approval again.")
        return

    # Download attachments for multimodal processing
    file_parts = []
    text_attachments = []  # text content extracted from .md/.txt/.py etc.
    SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
    # PDFs go directly to Gemini as binary parts
    SUPPORTED_DOC_TYPES = {"application/pdf"}
    # Text-based files are decoded and injected into the message
    SUPPORTED_TEXT_TYPES = {"text/plain", "text/markdown", "text/x-python", "text/csv",
                           "application/json", "text/x-c", "text/x-java", "text/html"}
    TEXT_EXTENSIONS = {".md", ".txt", ".py", ".json", ".csv", ".js", ".ts", ".yaml", ".yml",
                      ".toml", ".cfg", ".ini", ".sh", ".bat", ".xml", ".html", ".css", ".sql",
                      ".r", ".rs", ".go", ".java", ".c", ".cpp", ".h", ".rb", ".php", ".log"}
    # V3 3A — Audio/voice types for Whisper transcription
    AUDIO_TYPES = {"audio/ogg", "audio/mpeg", "audio/mp3", "audio/wav", "audio/webm", "audio/mp4", "audio/x-m4a"}
    AUDIO_EXTENSIONS = {".ogg", ".mp3", ".wav", ".m4a", ".webm", ".opus"}
    MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024  # 10MB cap per file

    from google.genai import types as genai_types

    for attachment in message.attachments:
        mime = (attachment.content_type or "").split(";")[0].strip()
        ext = Path(attachment.filename).suffix.lower() if attachment.filename else ""
        size = attachment.size or 0

        if size > MAX_ATTACHMENT_BYTES:
            logger.warning("Skipping oversized attachment %s (%d bytes)", attachment.filename, size)
            text_attachments.append(f"[Skipped {attachment.filename} — too large ({size // 1024 // 1024}MB)]")
            continue

        try:
            if mime in SUPPORTED_IMAGE_TYPES:
                # Images — send as Gemini multimodal parts
                img_bytes = await attachment.read()
                file_parts.append(genai_types.Part.from_bytes(
                    data=img_bytes, mime_type=mime,
                ))
                logger.info("Downloaded image: %s (%d bytes)", attachment.filename, len(img_bytes))

            elif mime in SUPPORTED_DOC_TYPES or ext == ".pdf":
                # PDFs — Gemini natively processes these
                pdf_bytes = await attachment.read()
                file_parts.append(genai_types.Part.from_bytes(
                    data=pdf_bytes, mime_type="application/pdf",
                ))
                logger.info("Downloaded PDF: %s (%d bytes)", attachment.filename, len(pdf_bytes))

            elif mime in SUPPORTED_TEXT_TYPES or ext in TEXT_EXTENSIONS:
                # Text-based files — decode and inject as text
                raw_bytes = await attachment.read()
                try:
                    text_content = raw_bytes.decode("utf-8", errors="replace")
                except Exception:
                    text_content = raw_bytes.decode("latin-1", errors="replace")
                # Cap individual text files at 15000 chars to fit in context
                if len(text_content) > 15000:
                    text_content = text_content[:15000] + "\n\n[File truncated — too long]"
                text_attachments.append(
                    f"[ATTACHED FILE: {attachment.filename}]\n{text_content}\n[END FILE: {attachment.filename}]"
                )
                logger.info("Downloaded text file: %s (%d chars)", attachment.filename, len(text_content))

            elif mime in AUDIO_TYPES or ext in AUDIO_EXTENSIONS:
                # V3 3A — Voice/audio: transcribe via OpenAI Whisper
                import io as _io
                audio_bytes = await attachment.read()
                logger.info("Downloaded audio: %s (%d bytes, mime=%s)", attachment.filename, len(audio_bytes), mime)
                try:
                    import openai as _openai
                    api_key = os.environ.get("OPENAI_API_KEY", "")
                    if not api_key:
                        logger.warning("OPENAI_API_KEY not set — cannot transcribe voice")
                        text_attachments.append("[Voice message received but transcription unavailable — OPENAI_API_KEY not set]")
                    else:
                        oai_client = _openai.OpenAI(api_key=api_key)
                        audio_file = _io.BytesIO(audio_bytes)
                        audio_file.name = attachment.filename or "voice.ogg"
                        transcript = oai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                        )
                        transcribed = transcript.text if transcript and transcript.text else ""
                        if transcribed:
                            text_attachments.append(f"[VOICE MESSAGE — transcribed]: {transcribed}")
                            logger.info("Transcribed voice: %d chars", len(transcribed))
                        else:
                            text_attachments.append("[Voice message received but transcription was empty]")
                except ImportError:
                    logger.warning("openai package not installed — cannot transcribe voice")
                    text_attachments.append("[Voice message received but openai package not installed]")
                except Exception as whisper_err:
                    logger.error("Whisper transcription failed: %s", whisper_err)
                    text_attachments.append(f"[Voice message received but transcription failed: {whisper_err}]")

            else:
                logger.info("Unsupported attachment type: %s (mime=%s, ext=%s)", attachment.filename, mime, ext)
                text_attachments.append(f"[Unsupported attachment: {attachment.filename} (type: {mime or ext})]")

        except Exception as e:
            logger.warning("Failed to download attachment %s: %s", attachment.filename, e)

    # Inject text attachments into the message content
    if text_attachments:
        attachment_block = "\n\n".join(text_attachments)
        if content:
            content = f"{content}\n\n{attachment_block}"
        else:
            content = attachment_block

    if not content and not file_parts:
        return

    if not content and file_parts:
        content = "The user sent file(s). Read and analyze them, then respond naturally."

    # Check agent is ready
    if vargas is None:
        await message.reply("I'm still waking up. Give me a moment.")
        return

    # Show typing indicator
    async with message.channel.typing():
        try:
            response = await vargas.respond(content, effective_channel_id, image_parts=file_parts if file_parts else None)

            # V3 1A — Collect screenshot attachments from agent loop
            discord_files = []
            screenshot_paths = vargas._agent_loop.get_screenshot_paths(effective_channel_id)
            for spath in screenshot_paths:
                try:
                    discord_files.append(discord.File(spath))
                    logger.info("Attaching screenshot: %s", spath)
                except Exception as fe:
                    logger.warning("Failed to attach screenshot %s: %s", spath, fe)

            # Split and send
            chunks = split_response(response)
            for i, chunk in enumerate(chunks):
                if i == 0:
                    # Attach screenshots to first reply if any
                    if discord_files:
                        await message.reply(chunk, files=discord_files)
                    else:
                        await message.reply(chunk)
                else:
                    await message.channel.send(chunk)

        except Exception as e:
            logger.error("Error processing message: %s", e)
            await message.reply("Something went sideways. Try again.")


def main():
    """Entry point for the Discord bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token or token.startswith("YOUR"):
        logger.error("DISCORD_TOKEN not set in .env file")
        logger.error("Edit project_vargas/.env and add your Discord bot token.")
        sys.exit(1)

    logger.info("Starting Vargas Discord bot...")
    client.run(token)


if __name__ == "__main__":
    main()
