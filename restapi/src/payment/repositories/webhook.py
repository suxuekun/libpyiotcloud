from shared.simple_api.repo import SimpleMongoBaseRepository

class WebhookRepository(SimpleMongoBaseRepository):
    def _create_indexes(self):
        self.collection.create_index([
                ('status',1),
                ('timestamp',-1)
            ],
            background=True)

