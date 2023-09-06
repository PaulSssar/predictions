import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import QuestionForm
from .models import Answer, Question


@login_required
def crystal_ball(request):
    """View-функция для страницы вопроса.
    Передает форму при GET-запросе. При POST-запросе
    сохраняет вопрос и перенаправляет на страницу с ответом"""
    form = QuestionForm(request.POST or None)
    if form.is_valid():
        text = form.cleaned_data['text']
        user = request.user
        Question.objects.create(
            text=text,
            user=user
        )
        return redirect('crystal_ball:answer', request.user.id)
    template = 'crystall_ball/question.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


def answer(request, id):
    """View-функция для страницы ответа.
    Передает данные о всех вопросах пользователя,
    количестве аналогичных вопросов и список последних 10
    вопросов текущего пользователя"""
    all_questions = Question.objects.filter(user_id=request.user)[:10]
    current_question = Question.objects.filter(user_id=request.user).last()
    count_current_q = Question.objects.filter(text=current_question.text).count()
    if request.user.id == id:
        answers = Answer.objects.all()
        answer = random.choice(answers)
        context = {
            'all_questions': all_questions,
            'answer': answer,
            'question': current_question,
            'count_q': count_current_q
        }
        return render(request, 'crystall_ball/answer.html', context)
    return redirect('crystal_ball:question')


def all_questions(request, id):
    """Список всех вопросов текущего пользователя"""
    all_questions = Question.objects.filter(user=request.user)
    context = {
        'all_questions': all_questions
    }
    template = 'crystall_ball/all_questions.html'
    return render(request, template, context)


