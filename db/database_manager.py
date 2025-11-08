import os
import json

class DatabaseManager:
    def __init__(self, base_dir="db"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        # Đường dẫn các file
        self.files = {
            "peers": os.path.join(self.base_dir, "peers.json"),
            "channels": os.path.join(self.base_dir, "channels.json"),
            "connections": os.path.join(self.base_dir, "peer_connections.json"),
            "direct_messages": os.path.join(self.base_dir, "direct_messages.json"),
        }

    def load_json(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DB] Error loading {path}: {e}")
            return {}

    def save_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[DB] Error saving {path}: {e}")

    def load_all(self):
        print("[DB] Loading all data from db/ ...")
        return {
            "peers": self.load_json(self.files["peers"]),
            "channels": self.load_json(self.files["channels"]),
            "connections": self.load_json(self.files["connections"]),
            "direct_messages": self.load_json(self.files["direct_messages"]),
        }

    def save_all(self, peers, channels, connections, direct_messages):
        print("[DB] Saving all data to db/ ...")
        self.save_json(self.files["peers"], peers)
        self.save_json(self.files["channels"], channels)
        self.save_json(self.files["connections"], connections)
        self.save_json(self.files["direct_messages"], direct_messages)
