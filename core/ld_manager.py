import json
import subprocess
import os
import time
import psutil
from typing import List, Dict, Optional
from .device import Device
from .exceptions import InstanceError, AppError
from utils.logger import logger
from config.settings import settings

class LDPlayerManager:
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.ld_path = "D:\\LDPlayer\\LDPlayer9\\ldconsole.exe"
        self.load_state()

    def execute_command(self, command: List[str]) -> str:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            raise InstanceError(f"Command failed: {e}")

    def create_instance(self, name: str, properties: Optional[Dict] = None) -> Device:
        if len(self.devices) >= settings.max_instances:
            raise InstanceError(f"Maximum number of instances ({settings.max_instances}) reached")

        props = properties or settings.default_properties
        command = [settings.ldplayer_path, "create", "--name", name]
        
        for key, value in props.items():
            command.extend([f"--{key}", str(value)])

        self.execute_command(command)
        
        device = Device(
            name=name,
            status="created",
            properties=props,
            index=len(self.devices)
        )
        self.devices[name] = device

        # Lưu state sau khi tạo instance
        self.save_state()
        
        logger.info(f"Created instance: {name}")
        return device

    def start_instance(self, name: str) -> bool:
        try:
            device = self.devices.get(name)
            if not device:
                raise InstanceError(f"Instance {name} does not exist")

            command = [self.ld_path, "launch", "--name", name]
            self.execute_command(command)
            device.status = "running"
            
            # Lưu state sau khi start
            self.save_state()
            
            logger.info(f"Started instance: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start instance {name}: {e}")
            raise

    def stop_instance(self, name: str):
        try:
            device = self.devices.get(name)
            if not device:
                raise InstanceError(f"Instance {name} does not exist")

            command = [self.ld_path, "quit", "--name", name]
            self.execute_command(command)
            device.status = "stopped"
            
            # Lưu state sau khi stop
            self.save_state()
            
            logger.info(f"Stopped instance: {name}")
        except Exception as e:
            logger.error(f"Failed to stop instance {name}: {e}")
            raise

    def install_app(self, name: str, apk_path: str):
        if name not in self.devices:
            raise InstanceError(f"Instance {name} does not exist")

        command = [settings.ldplayer_path, "install", "--name", name, "--apk", apk_path]
        self.execute_command(command)
        logger.info(f"Installed app on {name}: {apk_path}")

    def run_app(self, name: str, package_name: str):
        if name not in self.devices:
            raise InstanceError(f"Instance {name} does not exist")

        command = [settings.ldplayer_path, "launch", "--name", name, "--packagename", package_name]
        self.execute_command(command)
        logger.info(f"Running app on {name}: {package_name}")

    def save_state(self):
        state = {name: device.to_dict() for name, device in self.devices.items()}
        with open('data/instances.json', 'w') as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        try:
            # Tạo thư mục data nếu chưa tồn tại
            os.makedirs('data', exist_ok=True)
            
            # Kiểm tra file tồn tại
            if not os.path.exists('data/instances.json'):
                # Tạo file json trống nếu chưa có
                with open('data/instances.json', 'w') as f:
                    json.dump({}, f)
                self.devices = {}
                return

            # Đọc file json
            with open('data/instances.json', 'r') as f:
                state = json.load(f)
                self.devices = {
                    name: Device.from_dict(data) 
                    for name, data in state.items()
                }
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            self.devices = {}

    def get_instance_resources(self, name: str) -> Dict:
        """
        Lấy thông tin tài nguyên của một instance LDPlayer
        Args:
            name: Tên instance cần kiểm tra
        Returns:
            Dict chứa thông tin CPU, Memory, Threads và Status
        """
        try:
            # Kiểm tra instance có tồn tại
            cmd = [self.ld_path, "isrunning", "--name", name]
            result = self.execute_command(cmd)
            
            # Nếu instance không chạy, trả về trạng thái stopped
            if "running" not in result.lower():
                return {
                    'cpu': 0,
                    'memory': 0,
                    'threads': 0,
                    'status': 'stopped'
                }
            
            # Lấy danh sách processes của LDPlayer
            ldplayer_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'ldplayer' in proc.info['name'].lower() or 'dnplayer' in proc.info['name'].lower():
                        ldplayer_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
            # Tìm process chính của instance
            main_process = None
            for proc in ldplayer_processes:
                try:
                    cmdline = proc.cmdline()
                    if name in str(cmdline):
                        main_process = proc
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
            # Nếu tìm thấy process
            if main_process:
                try:
                    # Lấy thông tin tài nguyên
                    with main_process.oneshot():  # Tối ưu performance
                        cpu = main_process.cpu_percent(interval=0.5)
                        mem = main_process.memory_info().rss / 1024 / 1024  # Convert to MB
                        threads = main_process.num_threads()
                        
                        # Tính tổng tài nguyên của cả process con
                        children = main_process.children(recursive=True)
                        for child in children:
                            try:
                                cpu += child.cpu_percent(interval=0.1)
                                mem += child.memory_info().rss / 1024 / 1024
                                threads += child.num_threads()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                continue
                            
                        return {
                            'cpu': round(cpu, 1),
                            'memory': round(mem, 1),
                            'threads': threads,
                            'status': 'running'
                        }
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.error(f"Error accessing process info for {name}: {e}")
                
            # Nếu không tìm thấy process
            return {
                'cpu': 0,
                'memory': 0,
                'threads': 0,
                'status': 'error'
            }
            
        except Exception as e:
            logger.error(f"Failed to get resources for {name}: {e}")
            return {
                'cpu': 0,
                'memory': 0,
                'threads': 0,
                'status': 'error'
            }

    def get_all_instances_resources(self) -> Dict[str, Dict]:
        """
        Lấy thông tin tài nguyên của tất cả instances
        Returns:
            Dict[instance_name, resource_info]
        """
        resources = {}
        for name in self.devices:
            resources[name] = self.get_instance_resources(name)
        return resources

    def monitor_resources(self, threshold_cpu: int = 80, threshold_mem: int = 80):
        """
        Kiểm tra tài nguyên và cảnh báo nếu vượt ngưỡng
        Args:
            threshold_cpu: Ngưỡng CPU (%)
            threshold_mem: Ngưỡng Memory (%)
        """
        for name, resources in self.get_all_instances_resources().items():
            if resources['status'] == 'running':
                if resources['cpu'] > threshold_cpu:
                    logger.warning(f"High CPU usage in {name}: {resources['cpu']}%")
                if resources['memory'] > threshold_mem:
                    logger.warning(f"High memory usage in {name}: {resources['memory']}MB")

    