
from rest_framework import renderers, status


class BrandJSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            response_data = {
                'data': [],
                'success': False,
                'message': 'No brands added',
                'statusCode': 200

            }
        else:
            response_data = {
                'data': data,
                'success': True,
                'message': 'Brands listed successfully',
                'statusCode': 200

            }
        return super().render(response_data, accepted_media_type, renderer_context)

class CustomerProfileRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        success = False
        message = ""
        status_code = 200

        if data is None:
            message = "Customer profile not found"
            status_code = 404
        elif renderer_context['response'].status_code == 401:
            message = "Unauthorized access"
            status_code = 401
        else:
            success = True
            message = "Customer profile retrieved successfully"

        response_data = {
            'data': data,
            'success': success,
            'message': message,
            'statusCode': status_code

        }
        return super().render(response_data, accepted_media_type, renderer_context)


class CustomTokenObtainPairRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):

        if 'access' not in data:
            error_message = "Invalid username or password"
            status_code = status.HTTP_401_UNAUTHORIZED
        else:
            error_message = None
            status_code = status.HTTP_200_OK
        response_data = {
            'data': data.get('profileData', {}),
            'refreshToken': data.get('refresh'),
            'accessToken': data.get('access'),
            'success': error_message is None,
            'message': error_message or f'Welcome Back !',
            'statusCode': status_code,

        }
        return super().render(response_data, accepted_media_type, renderer_context)