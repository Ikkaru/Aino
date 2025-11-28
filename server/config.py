import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = PROJECT_ROOT/"config.yaml"

def load_config():
    # Load Config File
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = yaml.safe_load(f)
        print("Config Loaded")
        return settings
    except FileNotFoundError:
        print(f"ERROR: Config File '{CONFIG_FILE}' not found.")
        return {}
    except Exception as e:
        print(f"ERROR: error load config: {e}")
        return {}


CONFIG = load_config()

PATHS = CONFIG.get('paths', {})
PERSONA_FILE = PROJECT_ROOT/PATHS.get('PERSONA_FILE', 'data/server/prompt/persona.txt')
CHUNKING_INSTRUCTION = PROJECT_ROOT/PATHS.get('CHUNKING_INSTRUCTION', 'server/prompt/chunk_instruct.txt')
VOICE_MODEL = PROJECT_ROOT/PATHS.get('VOICE_MODEL', 'server/models/voice/')
HISTORY_FILE = PROJECT_ROOT/PATHS.get('CHAT_HISTORY', 'server/chat/chat_history.json')
CHUNK_FILE = PROJECT_ROOT/PATHS.get('CHAT_CHUNKS', 'server/chat/chat_chunks.json')
SETTINGS = CONFIG.get('settings', {})
MODEL = SETTINGS.get('MODEL', 'llama-3.1-8b-instant')
TEMPERATURE = SETTINGS.get('TEMPERATURE', '1')
SPEAKER_ID = SETTINGS.get('SPEAKER_ID', '0')
SPEED = SETTINGS.get('SPEED', '1')

print(HISTORY_FILE)