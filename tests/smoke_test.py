import time
import sys
from dataclasses import dataclass
from typing import Optional
import requests
from requests.exceptions import RequestException


@dataclass
class SmokeTestConfig:
    """Configuration for smoke test execution."""
    base_url: str = "http://127.0.0.1:8000"
    health_timeout: int = 20
    health_check_interval: int = 1
    request_timeout: int = 5
    test_user_id: str = "smoke_user"
    test_num_buckets: int = 10


class HealthCheckError(Exception):
    """Raised when service health check fails."""
    pass


class SmokeTestRunner:
    """Manages smoke test execution for the ML service."""
    
    def __init__(self, config: Optional[SmokeTestConfig] = None):
        self.config = config or SmokeTestConfig()
        self.session = requests.Session()
    
    def _check_health(self) -> bool:
        """Check if the service is healthy."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except RequestException:
            return False
    
    def wait_for_service(self) -> None:
        """Wait for the service to become available."""
        start_time = time.time()
        elapsed = 0
        
        while elapsed < self.config.health_timeout:
            if self._check_health():
                return
            time.sleep(self.config.health_check_interval)
            elapsed = time.time() - start_time
        
        raise HealthCheckError(
            f"Service at {self.config.base_url} did not become healthy "
            f"within {self.config.health_timeout} seconds"
        )
    
    def run_prediction_test(self) -> dict:
        """Execute the prediction endpoint test."""
        response = self.session.post(
            f"{self.config.base_url}/predict",
            json={
                "user_id": self.config.test_user_id,
                "num_buckets": self.config.test_num_buckets
            },
            timeout=self.config.request_timeout
        )
        response.raise_for_status()
        return response.json()
    
    def execute(self) -> int:
        """Run the complete smoke test suite."""
        try:
            self.wait_for_service()
            result = self.run_prediction_test()
            print(f"Smoke test passed: {result}")
            return 0
        except HealthCheckError as e:
            print(f"Health check failed: {e}")
            return 1
        except requests.HTTPError as e:
            print(f"Smoke test failed: HTTP {e.response.status_code} - {e.response.text}")
            return 1
        except RequestException as e:
            print(f"Smoke test failed: Request error - {e}")
            return 1
        except Exception as e:
            print(f"Smoke test failed: Unexpected error - {e}")
            return 1


def main() -> int:
    """Entry point for smoke test execution."""
    runner = SmokeTestRunner()
    return runner.execute()


if __name__ == "__main__":
    sys.exit(main())
