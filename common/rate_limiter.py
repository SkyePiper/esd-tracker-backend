"""Custom Rate Limiter to work around errors caused by default rate limiter"""

from fastapi.routing import APIRoute, _IncludedRouter
from fastapi_limiter.depends import RateLimiter
from starlette.requests import Request
from starlette.responses import Response

from common.helper_functions.errors import RateLimitedError


class CustomRateLimiter(RateLimiter):
    """Custom rate limiter to fix erroring behaviour"""

    @staticmethod
    def __get_routes_from_request(request: Request) -> list[APIRoute]:
        """Gets all the routes of the app

        :param request: The request to get
        :return: The routes
        """

        routes = []
        for route in request.app.routes:
            if isinstance(route, _IncludedRouter):
                routes += CustomRateLimiter.__get_routes(route)
            elif isinstance(route, APIRoute):
                routes.append(route)
            else:
                # We don't want to handle any other routes - They are not routes that we have defined!
                # They will probably be routes from FastAPI, which we do not want to handle
                pass

        return routes

    @staticmethod
    def __get_routes(router: _IncludedRouter) -> list[APIRoute]:
        """Gets all the routes from an included router

        :param router: The router to get the routes from
        :return: The routes
        """

        routes = []

        for route in router.original_router.routes:
            if isinstance(route, _IncludedRouter):
                routes += CustomRateLimiter.__get_routes(route)
            elif isinstance(route, APIRoute):
                routes.append(route)
            else:
                # We don't want to handle any other routes - They are not routes that we have defined!
                # They will probably be routes from FastAPI, which we do not want to handle
                pass

        return routes

    def __get_limiter_index(self, route: APIRoute) -> int:
        """Gets the index of the limiter dependency

        :return: The index of the limiter dependency
        """

        # Check if the route endpoint has _skip_limiter attribute
        if hasattr(route, "endpoint") and getattr(route.endpoint, "_skip_limiter", False):
            return -1

        for j, dependency in enumerate(route.dependencies):
            if self is dependency.dependency:
                return j

        return -1

    async def __call__(self, request: Request, response: Response):
        route_index = 0
        dep_index = 0
        for i, route in enumerate(self.__get_routes_from_request(request)):
            if route.path == request.scope["path"] and hasattr(route, "methods") and request.method in route.methods:
                route_index = i
                dep_index = self.__get_limiter_index(route)

        if dep_index != -1:
            rate_key = await self.identifier(request)
            key = f"{rate_key}:{route_index}:{dep_index}"
            success = await self.limiter.try_acquire_async(key, blocking=self.blocking)
            if not success:
                raise RateLimitedError()
