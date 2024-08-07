from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .models import UserAccount as User
from rest_framework.permissions import AllowAny  
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from .models import Organization, Person, Image
from .serializers import *
from django.shortcuts import get_object_or_404

class PersonOrganizationDetailsDeleteView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def delete(self, request, *args, **kwargs):
        person_id = kwargs.get('person_id')
        organization_id = kwargs.get('organization_id')

        try:
            detail = PersonOrganizationDetails.objects.get(Person_id=person_id, Organization_id=organization_id)
            detail.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PersonOrganizationDetails.DoesNotExist:
            return Response({'error': 'Details not found'}, status=status.HTTP_404_NOT_FOUND)
                           

class ApplyOrgView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id, org_id):
        try:

            if not user_id or not org_id:
                return Response(
                    {'error': 'user_id and org_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.get(id=user_id)
            organization = Organization.objects.get(id=org_id)
            person = Person.objects.get(User=user)

            candidate, created = Candidate.objects.get_or_create(Person=person, Organization=organization)

            if created:
                return Response(
                    {'message': 'Candidate successfully added to the organization!'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': 'Already applied to this organization.'},
                    status=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Person.DoesNotExist:
            return Response(
                {'error': 'Person not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error applying to organization: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserFormView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        try:
            data = request.data
            user = User.objects.get(id=user_id)
            person = Person.objects.get(User=user)
            
            person.date_of_birth = data.get('dateOfBirth')
            person.profession = data.get('profession')
            person.experience = data.get('experience')
            person.street_name = data.get('street')
            person.city = data.get('city')
            person.available_days = data.get('availableDays')
            person.available_times = data.get('availableTimes')
            person.modality = data.get('modality')
            person.topics = data.get('topics')
            person.goals = data.get('goals')
            person.motivations = data.get('motivations')
            person.save()

            user.is_form = True
            user.save()
            return Response({'message': 'Form data saved successfully!'}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RetrieveOrganizationExtView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            organization = Organization.objects.get(id=user_id)
            
            return Response(
                {'name': organization.name,
                 'description':organization.description,
                 'country':organization.country,
                 'userId':organization.User.id},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving organization: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RetrieveOrganizationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            organization = Organization.objects.get(User=user)
            
            return Response(
                {'name': organization.name,
                 'description':organization.description,
                 'country':organization.country},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Organization.DoesNotExist:
            return Response(
                {'error': 'Organization not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving organization: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RetrieveUserOrganizations(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            person = Person.objects.get(User=user)
            organizations = Organization.objects.filter(personorganizationdetails__Person=person)
            organization_serializer = OrganizationSerializer(organizations, many=True)
            return Response(
                {'organizations': organization_serializer.data},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Person.DoesNotExist:
            return Response(
                {'error': 'Person not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving organizations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RetrievePersonView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            person = Person.objects.get(User=user)
            person_serializer = PersonSerializer(person)
            user_serializer = UserSerializer(user) 
            return Response(
                {'person': person_serializer.data,
                 'user': user_serializer.data},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Person.DoesNotExist:
            return Response(
                {'error': 'Person not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving person: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        

class ApproveCandidate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, candidate_id):
        try:
            candidate = Candidate.objects.get(id=candidate_id)
            person = candidate.Person
            organization = candidate.Organization

            # Crear PersonOrganizationDetails
            PersonOrganizationDetails.objects.create(Person=person, Organization=organization)

            # Eliminar el candidato
            candidate.delete()

            return Response({'message': 'Candidate approved and added to organization'}, status=status.HTTP_200_OK)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RejectCandidate(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, candidate_id):
        try:
            candidate = Candidate.objects.get(id=candidate_id)
            candidate.delete()

            return Response({'message': 'Candidate rejected and deleted'}, status=status.HTTP_200_OK)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrgView(generics.ListAPIView):
    
    permission_classes = [AllowAny]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class CandidateDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, organization_id):
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        candidates = Candidate.objects.filter(Organization=organization)
        serializer = CandidateDetailSerializer(candidates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveImageOrgView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response(
                    {'error': 'User ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            organization = Organization.objects.get(id=user_id) 
            images = Image.objects.filter(User=organization.User)

            if images.exists():
                images_serializer = ImageSerializer(images, many=True)
                return Response(
                    {'images': images_serializer.data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'No images found for the specified user'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving image: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RetrieveImageView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
    
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response(
                    {'error': 'User ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.get(id=user_id)
            images = Image.objects.filter(User=user)

            if images.exists():
                images_serializer = ImageSerializer(images, many=True)
                return Response(
                    {'images': images_serializer.data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'No images found for the specified user'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error retrieving image: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UploadImageView(APIView):

    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = self.request.data
            user_id = data.get('user_id')                
            user = User.objects.get(id=user_id) 

            image = data['image']
            
            Image.objects.create(
                    image = image,
                    User = user
                )
            
            return Response(
                    {'success': 'Image Uploaded Successfully'},
                    status=status.HTTP_201_CREATED

                )
        except:
            return Response(
                {'error': 'Error Uploading Image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                
            )


class CreatePerson(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id)
            
            person = Person(
                phone_number=data.get('phone_number'),
                country=data.get('country'),
                description=data.get('description'),
                User=user  # Usuario obtenido por ID
            )
            person.save()

            return Response({'message': 'Person created successfully'}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateOrganization(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        try:
            data = request.data
            

            user_id = data.get('user_id')
            if not user_id:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Crear la organización
            organization = Organization(
                name=data.get('name'),
                description=data.get('description'),
                country=data.get('country'),
                website=data.get('website', ''),
                User=user
            )
            organization.save()

            return Response({'message': 'Organization created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# @method_decorator(csrf_exempt, name='dispatch')
class UserTypeUpdate(APIView):
    permission_classes = [AllowAny]  
    def patch(self, request, pk):
        try:
            data = json.loads(request.body)
            user = User.objects.get(pk=pk)
            user_type = data.get('user_type')
            is_completed = data.get('is_completed')

            if user_type is not None:
                user.user_type = user_type 
            if is_completed is not None:
                user.is_completed = is_completed

            user.save()
            return JsonResponse({'message': 'User updated successfully'}, status=200)
        except User.DoesNotExist:
            raise Http404("User not found")
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class CheckUserType(APIView):
    permission_classes = [AllowAny]  

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            return Response({'user_type': user.user_type})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


class CheckCompleteView(APIView):
    permission_classes = [AllowAny]  

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            return Response({'is_completed': user.is_completed})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        print(refresh_token)
        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView): 
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response


# tasksViews
class TaskListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            organization = Organization.objects.get(id=pk)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        tasks = Task.objects.filter(Organization=organization)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request, pk):
        
        try:
            organization = Organization.objects.get(id=pk)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['Organization'] = organization.id  # Asociar la tarea a la organización obtenida de la URL

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
        

    def put(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        
        serializer = TaskSerializer(task, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class OrganizationMembersView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, organization_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=organization_id)
        
        person_org_details = PersonOrganizationDetails.objects.filter(Organization=organization)
        members = [details.Person for details in person_org_details]
        
        serializer = PersonSerializer(members, many=True)
        return Response(serializer.data)

class EventListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            organization = Organization.objects.get(id=pk)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        events = Event.objects.filter(Organization=organization)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #Se puede postear un evento a la vez ya que, sino gernera erro en la linea 550
    def post(self, request, pk):
        
        try:
            organization = Organization.objects.get(id=pk)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['Organization'] = organization.id # Asociar la tarea a la organización obtenida de la URL

        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EventUpdateDestroyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            event = Event.objects.get(id=pk)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EventSerializer(event)
        return Response(serializer.data)
        

    def put(self, request, pk):
        try:
            event = Event.objects.get(id=pk)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        
        serializer = EventSerializer(event, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            event = Event.objects.get(id=pk)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
