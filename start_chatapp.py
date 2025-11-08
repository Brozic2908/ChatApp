#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# WeApRous release
#

"""
start_chatapp
~~~~~~~~~~~~~~~~~

This module provides the entry point for launching the hybrid chat application.
It combines client-server and P2P paradigms for distributed chat functionality.
"""

import json
import argparse
import threading
from datetime import datetime

from db.database_manager import DatabaseManager
from daemon.weaprous import WeApRous

PORT = 8001 # Default port for chat app

app = WeApRous()

# --- Database integration ---
db = DatabaseManager(base_dir="db")
loaded_data = db.load_all()

peers_registry = loaded_data.get("peers", {})
channels = loaded_data.get("channels", {})
peer_connections = loaded_data.get("connections", {})
direct_messages = loaded_data.get("direct_messages", {})

print(f"[DB] Loaded {len(peers_registry)} peers, {len(channels)} channels, "
      f"{len(direct_messages)} direct message threads.")

@app.route('/login', methods=['POST'])
def chat_login(headers="guest", body="anonymous"):
    """
    Handle user login for chat application.
    
    :param headers: Request headers
    :param body: Request body containing login credentials
    """
    print(f"[ChatApp] User login attempt - headers: {headers}, body: {body}")
    return {
        "status": "success",
        "message": "Logged in to chat"
    }


@app.route('/submit-info', methods=["POST"])
def submit_peer_info(headers="", body=""):
    """
    Register a new peer with the centralized server.
    
    Expected body format: {"peer_id": "peer123", "ip": "192.168.1.100", "port": 5000}
    
    :param headers: Request headers
    :param body: JSON containing peer information
    """
    try:
        data = json.loads(body) if body else {}
        peer_id = data.get("peer_id")
        peer_ip = data.get("ip")
        peer_port = data.get("port")
        
        if not peer_id or not peer_ip or not peer_port:
            print("[ChatApp] Invalid peer registration data")
            return {"status": "error", "message": "Missing required fields"}
        
        # Register peer
        peers_registry[peer_id] = {
            "ip": peer_ip,
            "port": peer_port,
            "last_seen": datetime.now().isoformat()
        }
        
        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        
        print(f"[ChatApp] Peer registered: {peer_id} at {peer_ip}:{peer_port}")
        print(f"[ChatApp] Total peers: {len(peers_registry)}")

        return {
            "status": "success",
            "message": "Peer registered",
            "peer_id": peer_id
        }
        
    except json.JSONDecodeError:
        print("[ChatApp] Invalid JSON in submit-info")
        return {"status": "error", "message": "Invalid JSON"}
    except Exception as e:
        print(f"[ChatApp] Error in submit-info: {e}")
        return {"status": "error", "message": str(e)}


@app.route("/get-list", methods=["GET"])
def get_peer_list(headers="", body=""):
    """
    Retrieve the list of active peers.
    
    :param headers: Request headers
    :param body: Request body (not used)
    :return: JSON list of active peers
    """
    print(f"[ChatApp] Peer list requested - total peers: {len(peers_registry)}")
    
    peer_list = []
    for peer_id, info in peers_registry.items():
        peer_list.append({
            "peer_id": peer_id,
            "ip": info["ip"],
            "port": info["port"],
            "last_seen": info["last_seen"],
        })
        
    db.save_all(peers_registry, channels, peer_connections, direct_messages)
    
    return {
        "status": "success",
        "peers": peer_list,
        "count": len(peer_list)
    }
    
@app.route("/add-list", methods=["POST"])
def add_to_channel(headers="", body=""):
    """
    Add a peer to a channel.
    
    Expected body: {"peer_id": "peer123", "channel": "general"}
    
    :param headers: Request headers
    :param body: JSON containing peer_id and channel name
    """
    try:
        data = json.loads(body) if body else {}
        peer_id = data.get("peer_id")
        channel_name = data.get("channel", "general")
        
        if not peer_id:
            return {"status": "error", "message": "peer_id"}
        
        # Create channel if doesn't exist
        if channel_name not in channels:
            channels[channel_name] = {
                "members": [],
                "messages": []
            }
        
        # Add peer to channel
        if peer_id not in channels[channel_name]["members"]:
            channels[channel_name]["members"].append(peer_id)

        # Track peer's channels
        if peer_id not in peer_connections:
            peer_connections[peer_id] = {"channels": []}
        if channel_name not in peer_connections[peer_id]["channels"]:
            peer_connections[peer_id]["channels"].append(channel_name)
        
        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        print(f"[ChatApp] Peer {peer_id} added to channel {channel_name}")
        
        return {
            "status": "success",
            "message": f"Added to channel {channel_name}",
            "channel": channel_name,
            "members_count": len(channels[channel_name]["members"])
        }
        
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}
    except Exception as e:
        print(f"[ChatApp] Error in add-list: {e}")
        return {"status": "error", "message": str(e)}


@app.route("/connect-peer", methods=["POST"])
def connect_to_peer(headers="", body=""):
    """
    Initiate P2P connection setup between peers.
    
    Expected body: {"from_peer": "peer123", "to_peer": "peer456"}
    
    :param headers: Request headers
    :param body: JSON containing source and destination peer IDs
    """
    try:
        data = json.loads(body) if body else {}
        from_peer = data.get("from_peer")
        to_peer=  data.get("to_peer")
        
        if not from_peer or not to_peer:
            return {"status": "error", "message": "Both from_peer and to_peer required"}
        
        # Check if peers exist
        if to_peer not in peers_registry:
            return {"status": "error", "message": "Target peer not found"}
        
        target_info = peers_registry[to_peer]
        
        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        
        print(f"[ChatApp] P2P connection: {from_peer} -> {to_peer}")

        return {
            "status": "success",
            "message": "Peer info retrieved",
            "peer_info": {
                "peer_id": to_peer,
                "ip": target_info["ip"],
                "port": target_info["port"]
            }
        }

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}
    except Exception as e:
        print(f"[ChatApp] Error in connect-peer: {e}")
        return {"status": "error", "message": str(e)}


@app.route("/broadcast-peer", methods=["POST"])
def broadcast_message(headers="", body=""):
    """
    Broadcast a message to all peers in a channel.
    
    Expected body: {"peer_id": "peer123", "channel": "general", "message": "Hello"}
    
    :param headers: Request headers
    :param body: JSON containing peer_id, channel, and message
    """
    try:
        data = json.loads(body) if body else {}
        peer_id = data.get('peer_id')
        channel_name = data.get('channel', 'general')
        message = data.get('message')

        if not peer_id or not message:
            return {"status": "error", "message": "peer_id and message required"}
        
        if channel_name not in channels:
            return {"status": "error", "message": "Channel not found"}
        
        # Store message
        message_obj = {
            "from": peer_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        channels[channel_name]['messages'].append(message_obj)
        
        # Get list of peers to broadcast to
        target_peers = [p for p in channels[channel_name]['members'] if p != peer_id]
        
        print(f"[ChatApp] Broadcast in {channel_name} from {peer_id}: {message}")
        print(f"[ChatApp] Broadcasting to {len(target_peers)} peers")

        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        return {
            "status": "success",
            "message": "Message broadcasted",
            "recipients": target_peers,
            "channel": channel_name
        }

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}
    except Exception as e:
        print(f"[ChatApp] Error in broadcast-peer: {e}")
        return {"status": "error", "message": str(e)}
    
    
@app.route('/send-peer', methods=['POST'])
def send_direct_message(headers="", body=""):
    """
    Send a direct message to a specific peer.
    
    Expected body: {"from_peer": "peer123", "to_peer": "peer456", "message": "Hi"}
    
    :param headers: Request headers
    :param body: JSON containing sender, receiver, and message
    """
    try:
        data = json.loads(body) if body else {}
        from_peer = data.get('from_peer')
        to_peer = data.get('to_peer')
        message = data.get('message')

        if not from_peer or not to_peer or not message:
            return {"status": "error", "message": "from_peer, to_peer, and message required"}
        
        if to_peer not in peers_registry:
            return {"status": "error", "message": "Target peer not found"}
        
        target_info = peers_registry[to_peer]
        # Tạo key cho direct messages (sắp xếp để đảm bảo consistency)
        dm_key = tuple(sorted([from_peer, to_peer]))
        
        # Khởi tạo nếu chưa tồn tại
        if dm_key not in direct_messages:
            direct_messages[dm_key] = []
        
        # Lưu message
        message_obj = {
            "from": from_peer,
            "to": to_peer,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        direct_messages[dm_key].append(message_obj)

        print(f"[ChatApp] Direct message {from_peer} -> {to_peer}: {message}")
        print(f"[ChatApp] Stored in DM key: {dm_key}, total messages: {len(direct_messages[dm_key])}")

        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        return {
            "status": "success",
            "message": "Message sent",
            "peer_info": {
                "peer_id": to_peer,
                "ip": target_info["ip"],
                "port": target_info["port"]
            }
        }

    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}
    except Exception as e:
        print(f"[ChatApp] Error in send-peer: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/get-direct-messages', methods=['GET', 'POST'])
def get_direct_messages(headers="", body=""):
    """
    Retrieve direct messages between two peers.
    
    Expected body: {"peer1": "peer123", "peer2": "peer456"}
    Hoặc chỉ cần {"from_peer": "peer123", "to_peer": "peer456"} (hoặc ngược lại)
    
    :param headers: Request headers
    :param body: JSON containing peer IDs
    """
    try:
        data = json.loads(body) if body else {}
        peer1 = data.get('peer1') or data.get('from_peer') or data.get('to_peer')
        peer2 = data.get('peer2') or data.get('to_peer') or data.get('from_peer')
        
        # Nếu chỉ có một peer, lấy peer còn lại từ current user
        if not peer1 or not peer2:
            return {"status": "error", "message": "Both peer IDs required"}
        
        # Tạo key (sắp xếp để đảm bảo consistency)
        dm_key = tuple(sorted([peer1, peer2]))
        
        if dm_key not in direct_messages:
            return {
                "status": "success",
                "peer1": peer1,
                "peer2": peer2,
                "messages": [],
                "count": 0
            }
        
        messages = direct_messages[dm_key]
        
        print(f"[ChatApp] Direct messages retrieved between {peer1} and {peer2}: {len(messages)}")
        
        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        return {
            "status": "success",
            "peer1": peer1,
            "peer2": peer2,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        print(f"[ChatApp] Error in get-direct-messages: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/get-messages', methods=['GET', 'POST'])
def get_channel_messages(headers="", body=""):
    """
    Retrieve messages from a channel.
    
    Expected query: ?channel=general
    
    :param headers: Request headers
    :param body: Request body (channel name can be in body or query)
    """
    try:
        # Try to parse channel from body
        data = json.loads(body) if body else {}
        channel_name = data.get('channel', 'general')
        
        if channel_name not in channels:
            return {
                "status": "success",
                "channel": channel_name,
                "messages": [],
                "count": 0
            }
        
        messages = channels[channel_name]["messages"]
        
        print(f"[ChatApp] Messages retrieved from {channel_name}: {len(messages)}")
        
        db.save_all(peers_registry, channels, peer_connections, direct_messages)
        return {
            "status": "success",
            "channel": channel_name,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        print(f"[ChatApp] Error in get-messages: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    """
    Entry point for launching the chat application server.
    
    :arg --server-ip (str): IP address to bind the server (default: 0.0.0.0).
    :arg --server-port (int): Port number to bind the server (default: 8001).
    """
    parser = argparse.ArgumentParser(
        prog='ChatApp',
        description='Hybrid Chat Application Server',
        epilog='Chat daemon combining client-server and P2P paradigms'
    )
    parser.add_argument(
        '--server-ip',
        type=str,
        default='0.0.0.0',
        help='IP address to bind the server. Default is 0.0.0.0'
    )
    parser.add_argument(
        '--server-port',
        type=int,
        default=PORT,
        help=f'Port number to bind the server. Default is {PORT}'
    )
 
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    # Prepare and launch the chat application
    print(f"[ChatApp] Starting hybrid chat server on {ip}:{port}")
    app.prepare_address(ip, port)
    app.run()