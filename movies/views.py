import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Movie, Rating
from .serializers import  MovieSerializer, RatingSerializer
from django.db.models import Avg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    
    def get_queryset(self):
        # Retrieve queryset of Movie objects from the database
        return Movie.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            self.update_data_json(serializer.data)  # Update data.json
            return Response({'message': 'Movie created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_data_json(self, movie_data):
        with open('data.json', 'r+') as file:
            data = json.load(file)
            movies_data = data.get('movies', [])
            movies_data.append(movie_data)
            data['movies'] = movies_data
            file.seek(0)
            json.dump(data, file, indent=4)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance_id = int(kwargs['pk'])
            instance = self.get_queryset().get(id=instance_id)
            self.perform_destroy(instance)
            return Response({'message': 'Movie deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'movie': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the movie to rate'),
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating value for the movie (1 to 5)'),
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user rating the movie'),
            }
        ),
        responses={status.HTTP_201_CREATED: RatingSerializer()},
    )
    def create(self, request, *args, **kwargs):
        # Extract values from request data
        movie_id = request.data.get('movie')
        rating_value = request.data.get('rating')
        user = request.data.get('userid')  # Assuming the key in request data is 'userid'

        # Check if all required fields are present
        if not all([movie_id, rating_value, user]):
            return Response({'error': 'All fields "movie", "rating", and "userid" are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the movie exists
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({'error': 'Movie with id {} does not exist'.format(movie_id)}, status=status.HTTP_404_NOT_FOUND)
        
        # Create or update the rating for the movie
        rating, created = Rating.objects.update_or_create(user=user, movie=movie, defaults={'rating': rating_value})
        
        # Serialize the rating object
        serializer = self.get_serializer(rating)
        
        # Return the serialized rating object
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class MovieSearchViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('query', openapi.IN_QUERY, description="Search query for movie name", type=openapi.TYPE_STRING),
    ],
    )
    def list(self, request):
        query = request.query_params.get('query', None)
        if not query:
            return Response({'error': 'Query parameter "query" is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        movies = Movie.objects.filter(name__icontains=query)
        if not movies.exists():
            return Response({'message': 'No movies found matching the query'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate the average rating for the found movies
        avg_rating = movies.aggregate(Avg('rating'))['rating__avg']
        
        serializer = MovieSerializer(movies, many=True)
        
        response_data = {
            'movies': serializer.data,
            'average_rating': avg_rating
        }
        
        return Response(response_data)







    # # Override the retrieve method to return movies from data.json
    # def retrieve(self, request, *args, **kwargs):
    #     try:
    #         movie_id = kwargs.get('pk')
    #         with open('data.json', 'r') as file:
    #             data = json.load(file)
    #             movies_data = data.get('movies', [])
    #             print(movies_data)
    #             for movie_data in movies_data:
    #                 if str(movie_data.get('id')) == movie_id:
    #                     serializer = self.get_serializer(data=movie_data)
    #                     serializer.is_valid(raise_exception=True)
    #                     return Response(serializer.data)
    #             return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # # Override the update method to update a movie
    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     self.write(serializer.data)
    #     return Response(serializer.data)
    
    # # Override the partial_update method to partially update a movie
    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     self.write(serializer.data)
    #     return Response(serializer.data)
    
    # # Override the destroy method to delete a movie
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)