from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Device:
    name: str
    status: str
    properties: Dict
    index: int
    pid: Optional[int] = None
    
    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "properties": self.properties,
            "index": self.index,
            "pid": self.pid
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            name=data["name"],
            status=data["status"],
            properties=data["properties"],
            index=data["index"],
            pid=data.get("pid")
        )