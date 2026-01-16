from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def health(self):
        self.client.get("/health/live")

    @task(1)
    def metrics(self):
        self.client.get("/metrics")
