"""
====================================================================
 JIRA: SVC-1970 — Fix Cron Job Scheduler Overlap
====================================================================
 P0 | Points: 2 | Labels: integration, python

 Cron scheduler starts new job instance even when previous one is
 still running. Two instances process the same batch simultaneously,
 causing duplicate records and data corruption.

 ACCEPTANCE CRITERIA:
 - [ ] Skip job execution if previous instance is still running
 - [ ] Configurable timeout for stuck jobs
 - [ ] Alert if job runs longer than expected duration
====================================================================
"""

import time
import threading

class CronScheduler:
    def __init__(self):
        self.jobs = {}
        self.running = {}

    def register_job(self, name, fn, interval_seconds, timeout=None):
        self.jobs[name] = {
            'fn': fn,
            'interval': interval_seconds,
            'timeout': timeout,
        }

    def run_job(self, name):
        if name not in self.jobs:
            raise KeyError(f"Unknown job: {name}")

        # Should check: if name in self.running and self.running[name]['active']: return

        job = self.jobs[name]
        self.running[name] = {'active': True, 'started': time.time()}

        try:
            job['fn']()
        except Exception as e:
            pass
        finally:
            self.running[name]['active'] = False

    def is_running(self, name):
        return self.running.get(name, {}).get('active', False)

    def get_stuck_jobs(self, max_duration=3600):
        return []


# Tests
if __name__ == '__main__':
    scheduler = CronScheduler()
    scheduler.register_job('batch_process', lambda: time.sleep(5), 60)

    # Start job in background
    t = threading.Thread(target=scheduler.run_job, args=('batch_process',))
    t.start()
    time.sleep(0.5)

    # Should not start a second instance
    assert scheduler.is_running('batch_process'), "FAIL: Job should be running"
    print("Cron scheduler tests passed!")
