"""
VARGAS V4 Snapshot Manager
Implements snapshot-first mutation protection for all write operations.
"""

import shutil
import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

class SnapshotManager:
    """
    Manages timestamped snapshots of target files/directories before write operations.
    Implements snapshot-first mutation protection.
    """
    
    def __init__(self, snapshots_dir: str = ".snapshots"):
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def create_snapshot(self, target_path: str) -> Dict[str, Any]:
        """
        Create a timestamped snapshot of the target file or directory.
        
        Args:
            target_path: Path to file or directory to snapshot
            
        Returns:
            Dict containing snapshot metadata and status
        """
        target = Path(target_path)
        
        if not target.exists():
            return {
                "success": False,
                "error": f"Target path does not exist: {target_path}",
                "snapshot_id": None
            }
            
        # Generate timestamp and snapshot ID
        timestamp = datetime.datetime.now().isoformat()
        snapshot_id = f"snapshot_{timestamp.replace(':', '-').replace('.', '-')}"
        snapshot_path = self.snapshots_dir / snapshot_id
        
        try:
            # Create snapshot directory
            snapshot_path.mkdir(exist_ok=True)
            
            # Copy target to snapshot
            if target.is_file():
                shutil.copy2(target, snapshot_path / target.name)
                snapshot_type = "file"
            elif target.is_dir():
                shutil.copytree(target, snapshot_path / target.name, dirs_exist_ok=True)
                snapshot_type = "directory"
            else:
                return {
                    "success": False,
                    "error": f"Unsupported target type: {target_path}",
                    "snapshot_id": None
                }
            
            # Create metadata file
            metadata = {
                "snapshot_id": snapshot_id,
                "timestamp": timestamp,
                "target_path": str(target.absolute()),
                "target_type": snapshot_type,
                "original_size": self._get_size(target),
                "created_by": "VARGAS V4 SnapshotManager"
            }
            
            metadata_path = snapshot_path / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            self.logger.info(f"Snapshot created: {snapshot_id} for {target_path}")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "snapshot_path": str(snapshot_path),
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create snapshot for {target_path}: {str(e)}")
            return {
                "success": False,
                "error": f"Snapshot creation failed: {str(e)}",
                "snapshot_id": None
            }
    
    def restore_snapshot(self, snapshot_id: str, target_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Restore a snapshot to its original location or specified target.
        
        Args:
            snapshot_id: ID of snapshot to restore
            target_path: Optional override path (defaults to original location)
            
        Returns:
            Dict containing restore operation status
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            return {
                "success": False,
                "error": f"Snapshot not found: {snapshot_id}"
            }
        
        try:
            # Load metadata
            metadata_path = snapshot_path / "metadata.json"
            if not metadata_path.exists():
                return {
                    "success": False,
                    "error": f"Snapshot metadata not found: {snapshot_id}"
                }
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Determine restore target
            restore_target = target_path if target_path else metadata["target_path"]
            restore_path = Path(restore_target)
            
            # Create backup of current state before restore
            if restore_path.exists():
                backup_id = f"pre_restore_{datetime.datetime.now().isoformat().replace(':', '-').replace('.', '-')}"
                backup_path = self.snapshots_dir / backup_id
                backup_path.mkdir(exist_ok=True)
                
                if restore_path.is_file():
                    shutil.copy2(restore_path, backup_path / restore_path.name)
                else:
                    shutil.copytree(restore_path, backup_path / restore_path.name, dirs_exist_ok=True)
            
            # Remove existing target if it exists
            if restore_path.exists():
                if restore_path.is_file():
                    restore_path.unlink()
                else:
                    shutil.rmtree(restore_path)
            
            # Restore from snapshot
            snapshot_content = snapshot_path / metadata["target_type"]
            if metadata["target_type"] == "file":
                shutil.copy2(snapshot_content, restore_path)
            else:  # directory
                shutil.copytree(snapshot_content, restore_path, dirs_exist_ok=True)
            
            self.logger.info(f"Snapshot restored: {snapshot_id} to {restore_target}")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "restored_to": str(restore_path.absolute()),
                "backup_created": backup_id if 'backup_id' in locals() else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to restore snapshot {snapshot_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Restore failed: {str(e)}",
                "snapshot_id": snapshot_id
            }
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """
        List all available snapshots with their metadata.
        
        Returns:
            List of snapshot metadata dictionaries
        """
        snapshots = []
        
        for snapshot_dir in self.snapshots_dir.iterdir():
            if snapshot_dir.is_dir() and snapshot_dir.name.startswith("snapshot_"):
                metadata_path = snapshot_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        snapshots.append(metadata)
                    except Exception as e:
                        self.logger.warning(f"Failed to read metadata for {snapshot_dir.name}: {str(e)}")
        
        # Sort by timestamp (newest first)
        snapshots.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return snapshots
    
    def delete_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Delete a snapshot directory and all its contents.
        
        Args:
            snapshot_id: ID of snapshot to delete
            
        Returns:
            Dict containing deletion status
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        
        if not snapshot_path.exists():
            return {
                "success": False,
                "error": f"Snapshot not found: {snapshot_id}"
            }
        
        try:
            shutil.rmtree(snapshot_path)
            self.logger.info(f"Snapshot deleted: {snapshot_id}")
            
            return {
                "success": True,
                "snapshot_id": snapshot_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to delete snapshot {snapshot_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Deletion failed: {str(e)}",
                "snapshot_id": snapshot_id
            }
    
    def _get_size(self, path: Path) -> int:
        """Calculate total size of file or directory."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
            return total
        return 0
    
    def get_snapshot_info(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific snapshot.
        
        Args:
            snapshot_id: ID of snapshot to query
            
        Returns:
            Snapshot metadata or None if not found
        """
        snapshot_path = self.snapshots_dir / snapshot_id
        metadata_path = snapshot_path / "metadata.json"
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Add current status information
            metadata["snapshot_exists"] = snapshot_path.exists()
            metadata["snapshot_size"] = self._get_size(snapshot_path)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get snapshot info for {snapshot_id}: {str(e)}")
            return None
