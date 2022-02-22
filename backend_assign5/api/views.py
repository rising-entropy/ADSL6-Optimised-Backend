from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
import jwt
from .models import *
import json
from datetime import datetime, timedelta
import pytz
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
utc=pytz.UTC
# Create your views here.

JWT_SECRET = 'HarryMaguire'
JWT_ALGORITHM = 'HS256'

def validateJWT(request):
    jwtToken = request.META['HTTP_AUTHORIZATION']
    try:
        validation = jwt.decode(jwtToken, 'HarryMaguire', algorithms="HS256")
        return True
    except:
        return False

class LoginAPI(APIView):

    def post(self, request):
        
        # JWT_EXP_DELTA_SECONDS = 2628000
        JWT_EXP_DELTA_SECONDS = 2628000
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        role = ""
        if user.groups.filter(name = 'student').exists():
            role = 'student'
        elif user.groups.filter(name = 'teacher').exists():
            role = 'teacher'
        if user is not None:
            payload = {
                'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
                'fName': user.first_name,
                'lName': user.last_name,
                'username': username,
                'role': role
            }
            
            jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
            
            return Response({"status": "200 OK", "username": username, "token": jwt_token})
        else:
            return Response({"status": "400 Bad Request", "message": "Invalid Password/Username"})


class QuizzesAPI(APIView):

    def post(self, request):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        name = request.data['name']
        theQuiz = Quiz(name=name)
        theQuiz.save()
        return Response({"status": "201 OK", "message": "Created Successfully!"})

    def get(self, request):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        theInstances = Quiz.objects.filter()
        theRequiredInstances = []
        for i in theInstances:
            theRequiredInstances.append({
                "id": i.id,
                "name": i.name
            })
        return Response(theRequiredInstances)

class QuizAPI(APIView):

    def post(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        theAnswers = request.data['answers']
        # {
        #     "id": 1,
        #     "answer": ""
        # }
        score = 0
        theQuiz = Quiz.objects.filter(id=id)[0]
        totalQuestionCount = len(Question.objects.filter(quiz=theQuiz))
        for k,v in theAnswers.items():
            theID = k
            theAnswer = v
            if Question.objects.filter(id=theID)[0].correctAnswer == theAnswer:
                score += 1
        userData = jwt.decode(request.META['HTTP_AUTHORIZATION'], JWT_SECRET, JWT_ALGORITHM)
        theUsername = ""
        for k,v in userData.items():
            if k=='username':
                theUsername=v
        theUser = User.objects.filter(username=theUsername)[0]
        newScore = Score(score=score, questionCount=totalQuestionCount, student=theUser, quiz=theQuiz)
        newScore.save()

        return Response({
            "score": score,
            "questions": totalQuestionCount,
            "quiz": theQuiz.name
        })

    def get(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        theQuizInstance = Quiz.objects.filter(id=id)[0]
        quizName = theQuizInstance.name
        theQuestions = Question.objects.filter(quiz=theQuizInstance)
        theRequiredQuestions = []
        for i in theQuestions:
            theRequiredQuestions.append({
                "id": i.id,
                "question": i.question,
                "imageLink": i.imageLink,
                "option1": i.option1,
                "option2": i.option2,
                "option3": i.option3,
                "option4": i.option4,
            })
        return Response({"questions": theRequiredQuestions, "name": quizName})
    
    def put(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        
        name = request.data['name']
        
        Quiz.objects.filter(id=id).update(name=name)
        
        return Response({"status": "200 OK", "message": "Updated Successfully!"})

    def delete(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        
        Quiz.objects.filter(id=id).delete()
        
        return Response({"status": "200 OK", "message": "Deleted Successfully!"})
    
class QuestionsAPI(APIView):
    
    def post(self, request):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        quiz = request.data['quizID']
        quiz = Quiz.objects.filter(id = quiz)[0]
        question = request.data['question']
        imageLink = request.data['imageLink']
        option1 = request.data['option1']
        option2 = request.data['option2']
        option3 = request.data['option3']
        option4 = request.data['option4']
        correctAnswer = request.data['correctAnswer']
        
        theQuestion = Question(quiz=quiz,question=question,imageLink=imageLink,option1=option1,option2=option2,option3=option3,option4=option4,correctAnswer=correctAnswer)
        theQuestion.save()
        return Response({"status": "201 OK", "message": "Created Successfully!"})

    def get(self, request):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        
        # theQuestions = Question.objects.filter()
        theQuestions = Question.objects.select_related("quiz").all()
        
        theRequiredQuestions = []
        for i in theQuestions:
            theRequiredQuestions.append({
                "id": i.id,
                "question": i.question,
                "imageLink": i.imageLink,
                "option1": i.option1,
                "option2": i.option2,
                "option3": i.option3,
                "option4": i.option4,
                "correctAnswer": i.correctAnswer,
                "quiz": i.quiz.name
            })
        return Response(theRequiredQuestions)


class QuestionAPI(APIView):
    
    def get(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        theQuestion = Question.objects.filter(id=id)[0]
        theQuestion = {
            "id": theQuestion.id,
            "question": theQuestion.question,
            "imageLink": theQuestion.imageLink,
            "option1": theQuestion.option1,
            "option2": theQuestion.option2,
            "option3": theQuestion.option3,
            "option4": theQuestion.option4,
            "correctAnswer": theQuestion.correctAnswer,
            "quizID": theQuestion.quiz.id
        }
        return Response(theQuestion)
    
    def put(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        quiz = request.data['quizID']
        quiz = Quiz.objects.filter(id = quiz)[0]
        question = request.data['question']
        imageLink = request.data['imageLink']
        option1 = request.data['option1']
        option2 = request.data['option2']
        option3 = request.data['option3']
        option4 = request.data['option4']
        correctAnswer = request.data['correctAnswer']
        Question.objects.filter(id=id).update(quiz=quiz,question=question,imageLink=imageLink,option1=option1,option2=option2,option3=option3,option4=option4,correctAnswer=correctAnswer)
        
        return Response({"status": "200 OK", "message": "Updated Successfully!"})
 
    def delete(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        Question.objects.filter(id=id).delete()
        return Response({"status": "200 OK", "message": "Deleted Successfully!"})

class ScoresAPI(APIView):

    def get(self, request, id):
        if validateJWT(request) is False:
                return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        theQuiz=Quiz.objects.filter(id=id)[0]
        theInstances = Score.objects.filter(quiz=theQuiz)
        theRequiredInstances = []
        for i in theInstances:
            theRequiredInstances.append({
                "quiz": i.quiz.name,
                "score": i.score,
                "questions": i.questionCount,
                "username": i.student.username,
                "name": i.student.first_name+" "+i.student.last_name
            })
        return Response(theRequiredInstances)

class Questions2API(APIView):
    def get(self, request, id):
        # if validateJWT(request) is False:
        #     return Response({"status": "401 Unauthorized", "message": "authentication token invalid."})
        theQuiz = Quiz.objects.filter(id=id)[0]
        theQuestions = Question.objects.filter(quiz=theQuiz)
        theRequiredQuestions = []
        for i in theQuestions:
            theRequiredQuestions.append({
                "id": i.id,
                "question": i.question,
                "imageLink": i.imageLink,
                "option1": i.option1,
                "option2": i.option2,
                "option3": i.option3,
                "option4": i.option4,
                "correctAnswer": i.correctAnswer,
                "quiz": i.quiz.name
            })
        return Response(theRequiredQuestions)