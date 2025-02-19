from core.ld_manager import LDPlayerManager
from utils.logger import logger
import time

class Automation:
    def __init__(self, manager: LDPlayerManager):
        self.manager = manager

    def batch_create_instances(self, count: int):
        for i in range(count):
            name = f"instance_{i}"
            try:
                device = self.manager.create_instance(name)
                self.manager.start_instance(name)
                time.sleep(5)  # Wait for instance to start
            except Exception as e:
                logger.error(f"Failed to create/start instance {name}: {e}")

    def batch_install_app(self, apk_path: str):
        for name in self.manager.devices:
            try:
                self.manager.install_app(name, apk_path)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to install app on {name}: {e}")

    def batch_run_app(self, package_name: str):
        for name in self.manager.devices:
            try:
                self.manager.run_app(name, package_name)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to run app on {name}: {e}")