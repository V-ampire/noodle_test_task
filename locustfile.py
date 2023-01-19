from locust import HttpUser, task

class GetGroupUser(HttpUser):
    @task
    def get_group(self):
        self.client.get("/vk/group/76746437/")
