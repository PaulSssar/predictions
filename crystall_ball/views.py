import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import QuestionForm
from .models import Answer, Question, Cards
from .service import get_tarot_interpretation
from log import log


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
        'form': form
    }
    return render(request, template, context)


def answer(request, id):
    """View-функция для страницы ответа.
    Передает данные о всех вопросах пользователя,
    количестве аналогичных вопросов, список последних 10
    вопросов текущего пользователя и AI-трактовку расклада."""

    all_questions = Question.objects.filter(user_id=request.user)[:10]
    current_question = Question.objects.filter(user_id=request.user).last()

    if not current_question:
        return redirect('crystal_ball:question')

    count_current_q = Question.objects.filter(text=current_question.text).count()

    if request.user.id == id:
        all_cards = Cards.objects.all()
        cards = random.sample(list(all_cards), 3)
        log.info(f'CARDS ANSWERS: {cards}')

        # Генерация трактовки через GigaChat
        card_names = [card.name for card in cards]
        interpretation = get_tarot_interpretation(card_names)

        # Сохранение ответа в базу данных
        answer_obj = Answer.objects.create(
            question=current_question,
            text=interpretation,
        )

        context = {
            'all_questions': all_questions,
            'answer': answer_obj.text,
            'question': current_question,
            'count_q': count_current_q,
            'cards': cards,
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


