import json
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core import management
from django.http import HttpRequest, JsonResponse
from django.middleware.csrf import get_token
from django.views import View


class CreateUserView(View):
    """A view for creating a user via HTTP POST requests."""

    def post(
        self,
        request: HttpRequest,
    ) -> JsonResponse:
        """Handle HTTP POST requests to create a user.

        Args:
        ----
        request (HttpRequest): The HTTP request object containing the user data.

        Returns:
        -------
        JsonResponse: A JSON response indicating the success of the user creation.
        """
        body = json.loads(request.body.decode("utf-8"))

        try:
            user_model = get_user_model()
            user = user_model.objects.create_user(**body)
            return JsonResponse({"user_id": user.id}, status=HTTPStatus.CREATED)
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=HTTPStatus.BAD_REQUEST
            )


class RefreshDatabaseView(View):
    """A view for running Django's flush command via HTTP POST requests."""

    def post(
        self,
        _: HttpRequest,
    ) -> JsonResponse:
        """Handle HTTP POST requests to execute Django's flush command.

        Args:
        ----
        request (HttpRequest): The HTTP request object.

        Returns:
        -------
        JsonResponse: A JSON response indicating the success of the command execution.
        """
        management.call_command("flush", "--no-input")

        return JsonResponse({"success": True})


class MigrateView(View):
    """A view for running Django's migrate command via HTTP POST requests."""

    def post(
        self,
        _: HttpRequest,
    ) -> JsonResponse:
        """Handle HTTP POST requests to execute Django's migrate command.

        Args:
        ----
        request (HttpRequest): The HTTP request object.

        Returns:
        -------
        JsonResponse: A JSON response indicating the success of the command execution.
        """
        management.call_command("migrate")

        return JsonResponse({"success": True})


class ManageView(View):
    """A view for running Django management commands via HTTP POST requests."""

    def post(
        self,
        request: HttpRequest,
    ) -> JsonResponse:
        """Handle HTTP POST requests to execute Django management commands.

        Args:
        ----
        request (HttpRequest): The HTTP request object containing the command to execute.

        Returns:
        -------
        JsonResponse: A JSON response indicating the success of the command execution.
        """
        body = json.loads(request.body.decode("utf-8"))
        command = body.get("command")
        parameters = body.get("parameters")
        management.call_command(
            command,
            *parameters,
        )

        return JsonResponse({"success": True})


class CSRFTokenView(View):
    """A view for retrieving the CSRF token via HTTP GET requests."""

    def get(
        self,
        request: HttpRequest,
    ) -> JsonResponse:
        """Handle HTTP GET requests to retrieve the CSRF token.

        Args:
        ----
        request (HttpRequest): The HTTP request object.

        Returns:
        -------
        JsonResponse: A JSON response containing the CSRF token.
        """
        token = get_token(request)

        return JsonResponse({"token": token})
