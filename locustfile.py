from locust import HttpUser, task

class GetGroupUser(HttpUser):
    @task
    def get_group(self):
        self.client.get("/vk/group/76746437/")
        self.client.get("/vk/group/53956001/")
        self.client.get("/vk/group/69108280/")
