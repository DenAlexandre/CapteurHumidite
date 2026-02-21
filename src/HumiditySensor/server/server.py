#!/usr/bin/sudo python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Controllers'))
import SensorController as SensorController
import const

def main():
    try:
        _controller = SensorController.SensorController()
        return sys.exit(_controller.run_app())
    except Exception as exc:
        raise RuntimeError from exc

if __name__ == '__main__':
    sys.exit(main())


