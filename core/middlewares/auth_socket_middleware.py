from channels.middleware import BaseMiddleware


class AuthSocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        token = (
            dict(
                [item.split('=') for item in scope['query_string'].decode('utf-8').split('&') if item]
            ).get('token', None)
        )
        print(token)
        return await super().__call__(scope, receive, send)



